r"""Helper function for sequences generation.

Usage:
    import lmp

    generated = lmp.util.generate_sequence(...)
    generated = lmp.util.generate_sequence_by_config(...)
"""

# built-in modules

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from typing import List

# 3rd-party modules

import torch

# self-made modules

import lmp.config
import lmp.model
import lmp.tokenizer


@torch.no_grad()
def generate_sequence(
        beam_width: int,
        begin_of_sequence: str,
        device: torch.device,
        max_seq_len: int,
        model: lmp.model.BaseRNNModel,
        tokenizer: lmp.tokenizer.BaseTokenizer
) -> List[str]:
    r"""Sequences generation using beam search.

    Args:
        beam_width:
            Number of candidate sequences to output.
        begin_of_sequence:
            Begining of sequence which model will auto-complete.
        device:
            Model running device.
        max_seq_len:
            Maximum of output sequences length.
        model:
            Language model.
        tokenizer:
            Tokenizer for encoding and decoding sequences.

    Returns:
        Generated sequences.
    """
    # Evaluation mode.
    model.eval()

    # Encode sequence and convert into tensor. Remove [EOS] since we are using
    # begin of sentence.
    cur_seq = tokenizer.encode(begin_of_sequence, max_seq_len=-1)
    cur_seq = torch.LongTensor(cur_seq)[:-1].to(device)

    # Get begin sequence length.
    seq_len = cur_seq.size(-1)

    # Generated sequence.
    # Start shape (1, S).
    # Final shape (B, S).
    cur_seq = cur_seq.reshape(1, seq_len)

    # Accumulated negative log-likelihood. Using log can change consecutive
    # probability multiplication into sum of log probability which can
    # avoid computational underflow. Initialized to zero with shape (B).
    accum_prob = torch.zeros(beam_width).to(device)

    for _ in range(max_seq_len - seq_len):
        # Model prediction has shape (B, S, V).
        pred_y = model.predict(cur_seq)

        # Record all beams prediction.
        # Each beam will predict `beam_width` different results.
        # So we totally have `beam_width * beam_width` different results.
        top_k_in_all_beams = []
        for out_beam in range(cur_seq.size(0)):
            # Get `beam_width` different prediction from beam `out_beam`.
            # `top_k_prob_in_beam` has shape (B) and
            # `top_k_index_in_beam` has shape (B).
            top_k_prob_in_beam, top_k_index_in_beam = \
                pred_y[out_beam, -1].topk(
                    k=beam_width,
                    dim=-1
                )

            # Record each beam's negative log-likelihood and concate
            # next token id based on prediction.
            for in_beam in range(beam_width):
                # Accumulate negative log-likelihood. Since log out
                # negative value when input is in range 0~1, we negate it
                # to be postive.
                prob = accum_prob[out_beam] - \
                    top_k_prob_in_beam[in_beam].log()
                prob = prob.unsqueeze(0)

                # Concate next predicted token id.
                seq = torch.cat([
                    cur_seq[out_beam],
                    top_k_index_in_beam[in_beam].unsqueeze(0)
                ], dim=-1).unsqueeze(0)

                # Record result.
                top_k_in_all_beams.append({
                    'prob': prob,
                    'seq': seq
                })

        # Compare each recorded result in all beams. First concate tensor
        # then use `topk` to get the `beam_width` highest prediction in all
        # beams.
        _, top_k_index_in_all_beams = torch.cat([
            beam['prob']
            for beam in top_k_in_all_beams
        ]).topk(k=beam_width, dim=0)

        # Update `cur_seq` which is the `beam_width` highest results.
        cur_seq = torch.cat([
            top_k_in_all_beams[index]['seq']
            for index in top_k_index_in_all_beams
        ], dim=0)

        # Update accumlated negative log-likelihood.
        accum_prob = torch.cat([
            top_k_in_all_beams[index]['prob']
            for index in top_k_index_in_all_beams
        ], dim=0)

    return tokenizer.batch_decode(cur_seq.tolist())


def generate_sequence_by_config(
        beam_width: int,
        begin_of_sequence: str,
        config: lmp.config.BaseConfig,
        max_seq_len: int,
        model: lmp.model.BaseRNNModel,
        tokenizer: lmp.tokenizer.BaseTokenizer
) -> List[str]:
    r"""Helper function for sequences generation.

    Args:
        beam_width:
            Number of candidate sequences to output.
        begin_of_sequence:
            Begining of sequence which model will auto-complete.
        config:
            Configuration object with attributes `device`.
        max_seq_len:
            Maximum of output sequences length.
        model:
            Language model.
        tokenizer:
            Tokenizer for encoding and decoding sequences.

    Returns:
        Generated sequences.
    """

    return generate_sequence(
        beam_width=beam_width,
        begin_of_sequence=begin_of_sequence,
        device=config.device,
        max_seq_len=max_seq_len,
        model=model,
        tokenizer=tokenizer
    )
