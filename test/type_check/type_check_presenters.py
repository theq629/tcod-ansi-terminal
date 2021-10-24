from tcod_ansi_terminal.context import Presenter, NaivePresenter, SparsePresenter

def _use_presenter(presenter: Presenter) -> None:
    pass

def _use_naive_presenter(presenter: NaivePresenter) -> None:
    _use_presenter(presenter)

def _use_sparse_presenter(presenter: SparsePresenter) -> None:
    _use_presenter(presenter)
