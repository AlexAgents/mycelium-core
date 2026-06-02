from src.core.app_controller import (
    AppController,
)


def test_controller_creation():

    controller = AppController()

    assert controller is not None

    assert controller.session is not None


def test_session_creation():

    controller = AppController()

    session = controller.create_session()

    assert session is not None

    assert (
        controller.session.session_id
        == session
    )


def test_generate_voters():

    controller = AppController()

    voters = controller.generate_voters(
        5
    )

    assert len(voters) == 5