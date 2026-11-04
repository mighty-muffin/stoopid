"""Example: use stoopid as a library from another project."""

import stoopid


def main() -> None:
    print(f"stoopid {stoopid.__version__}")
    print(f"add(1, 2)      = {stoopid.add(1, 2)}")
    print(f"multiply(3, 4) = {stoopid.multiply(3, 4)}")
    print(f"fibonacci(10)  = {stoopid.fibonacci(10)}")

    try:
        stoopid.fibonacci(-1)
    except ValueError as exc:
        print(f"fibonacci(-1)  -> ValueError: {exc}")


if __name__ == "__main__":
    main()
