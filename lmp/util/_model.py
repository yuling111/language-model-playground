r"""Helper function for loading model.

Usage:
    import lmp

    model = lmp.util.load_model(...)
    model = lmp.util.load_model_by_config(...)
"""

# built-in modules

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os

# 3rd-party modules

import torch

# self-made modules

import lmp.config
import lmp.model
import lmp.tokenizer


def load_model(
        checkpoint: int,
        d_emb: int,
        d_hid: int,
        device: torch.device,
        dropout: float,
        experiment: str,
        model_class: str,
        num_linear_layers: int,
        num_rnn_layers: int,
        pad_token_id: int,
        vocab_size: int
) -> lmp.model.BaseRNNModel:
    r"""Helper function for constructing language model.

    Load optimizer from pre-trained checkpoint when `checkpoint != -1`.

    Args:
        checkpoint:
            Pre-trained model's checkpoint.
        d_emb:
            Embedding matrix vector dimension.
        d_hid:
            GRU layers hidden dimension.
        device:
            Model running device.
        dropout:
            Dropout probability on all layers out (except output layer).
        experiment:
            Name of the pre-trained experiment.
        num_rnn_layers:
            Number of GRU layers to use.
        num_linear_layers:
            Number of Linear layers to use.
        pad_token_id:
            Padding token's id. Embedding layers will initialize padding
            token's vector with zeros.
        vocab_size:
            Embedding matrix vocabulary dimension.

    Raises:
        ValueError:
            If `model` does not supported.

    Returns:
        `lmp.model.BaseRNNModel` if `model_class == 'rnn'`;
        `lmp.model.GRUModel` if `model_class == 'gru'`;
        `lmp.model.LSTMModel` if `model_class == 'lstm'`.
    """

    if model_class == 'rnn':
        model = lmp.model.BaseRNNModel(
            d_emb=d_emb,
            d_hid=d_hid,
            dropout=dropout,
            num_rnn_layers=num_rnn_layers,
            num_linear_layers=num_linear_layers,
            pad_token_id=pad_token_id,
            vocab_size=vocab_size
        )
    elif model_class == 'gru':
        model = lmp.model.GRUModel(
            d_emb=d_emb,
            d_hid=d_hid,
            dropout=dropout,
            num_rnn_layers=num_rnn_layers,
            num_linear_layers=num_linear_layers,
            pad_token_id=pad_token_id,
            vocab_size=vocab_size
        )
    elif model_class == 'lstm':
        model = lmp.model.LSTMModel(
            d_emb=d_emb,
            d_hid=d_hid,
            dropout=dropout,
            num_rnn_layers=num_rnn_layers,
            num_linear_layers=num_linear_layers,
            pad_token_id=pad_token_id,
            vocab_size=vocab_size
        )
    else:
        raise ValueError(
            f'model `{model_class}` does not support.\nSupported options:' +
            ''.join(list(map(
                lambda option: f'\n\t--model {option}',
                [
                    'rnn',
                    'gru',
                    'lstm',
                ]
            )))
        )

    if checkpoint != -1:
        file_path = f'{lmp.path.DATA_PATH}/{experiment}/model-{checkpoint}.pt'
        if not os.path.exists(file_path):
            raise FileNotFoundError(f'file {file_path} does not exist.')
        model.load_state_dict(torch.load(file_path))

    return model.to(device)


def load_model_by_config(
        checkpoint: int,
        config: lmp.config.BaseConfig,
        tokenizer: lmp.tokenizer.BaseTokenizer
) -> lmp.model.BaseRNNModel:
    r"""Helper function for constructing language model.

    Load model from pre-trained checkpoint when `checkpoint != -1`.

    Args:
        checkpoint:
            Pre-trained model's checkpoint.
        config:
            Configuration object with attributes `d_emb`, `d_hid`, `dropout`,
            `device`, `experiment`, `model_class`, `num_linear_layer` and
            `num_rnn_layer`.
        tokenizer:
            Tokenizer object with attributes `pad_token_id` and `vocab_size`.

    Returns:
        Same as `load_model`.
    """
    return load_model(
        checkpoint=checkpoint,
        d_emb=config.d_emb,
        d_hid=config.d_hid,
        device=config.device,
        dropout=config.dropout,
        experiment=config.experiment,
        model_class=config.model_class,
        num_linear_layers=config.num_linear_layers,
        num_rnn_layers=config.num_rnn_layers,
        pad_token_id=tokenizer.convert_token_to_id(tokenizer.pad_token),
        vocab_size=tokenizer.vocab_size
    )
