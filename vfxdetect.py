"""This is a convenience/backwards-compatibility script, and simply provides an
alternative to running scenedetect from source.
"""

if __name__ == "__main__":
    # pylint: disable=no-name-in-module
    from scenedetect.__main__ import main
    main()
