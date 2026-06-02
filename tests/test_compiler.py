from src.core.compiler_service import (
    CompilerService,
)


def test_compile_contract():

    compiler = CompilerService()

    abi, bytecode = (
        compiler.compile_contract()
    )

    assert isinstance(abi, list)

    assert isinstance(bytecode, str)

    assert len(bytecode) > 100