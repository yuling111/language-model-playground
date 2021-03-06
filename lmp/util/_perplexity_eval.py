r"""Helper function for calculating perplexity.

Usage:
    import lmp

    generated = lmp.util.batch_perplexity_eval(...)
    generated = lmp.util.perplexity_eval(...)
"""

# built-in modules

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from typing import List

# 3rd-party modules

import torch

from tqdm import tqdm

# self-made modules

import lmp.model
import lmp.tokenizer


@torch.no_grad()
def perplexity_eval(
        device: torch.device,
        model: lmp.model.BaseRNNModel,
        sequence: str,
        tokenizer: lmp.tokenizer.BaseTokenizer
) -> float:
    r"""Helper function for calculating perplexity.

    Args:
        device:
            Model running device.
        model:
            Language model.
        sequence:
            Sequence for evaluation.
        tokenizer:
            Tokenizer for encoding sequence.

    Return:
        Perplexity of `sequence`.
    """
    # Evalation mode.
    model.eval()

    # Encode sequence and convert into tensor. Original sequence length: S.
    # New sequence length: S + 2.
    sequence = tokenizer.encode(sequence, max_seq_len=-1)

    # `sequence[:-2]` means predict tokens include [BOS] output but exclude
    # [EOS] input. `x.shape = (S)`.
    x = torch.LongTensor(sequence[:-2]).to(device)

    # `y.shape = (S)`.
    y = sequence[1:-1]

    # Reshape into `(1, S)` to fit model.
    x = x.reshape(1, -1)

    # Get model vocabulary prediction with shape `(1, S, V)`.
    pred_y = model.predict(x)

    # Reshape into `(S)` for easier maniplation.
    x = x.squeeze(0)

    # Reshape into `(S, V)` for easier maniplation.
    pred_y = pred_y.squeeze(0)

    # Accumulate negative log-likelihood.
    nll = torch.zeros(1).to(device)

    # Iterate through each prediction.
    for pos, token_id in enumerate(y):
        probs = pred_y[pos, token_id]
        nll = nll - torch.log(probs)

    # Normalized by length.
    nll = nll / x.size(0)

    # Take exponential to cancel logarithmic.
    return nll.exp().item()


def batch_perplexity_eval(
        dataset: List[str],
        device: torch.device,
        model: lmp.model.BaseRNNModel,
        tokenizer: lmp.tokenizer.BaseTokenizer
) -> List[float]:
    r"""Helper function for calculating dataset perplexity.

    Args:
        dataset:
            Evaluating each sequence in the dataset.
        device:
            Model running device.
        model:
            Language model.
        tokenizer:
            Tokenizer for encoding sequence.
    Return:
        Perplexity of `dataset`.
    """
    dataset_iterator = tqdm(
        dataset,
        desc='Calculating perplexities'
    )
    perplexties = []

    for sequence in dataset_iterator:
        perplexity = perplexity_eval(
            device=device,
            model=model,
            sequence=sequence,
            tokenizer=tokenizer
        )
        perplexties.append(perplexity)

    return perplexties
