import os
import sys

try:
    import stat
except ImportError:
    stat = None


def nag():
    """
    Check if pre-commits should be installed for this repository.
    If they are not and should be then annoy the developer.
    To be called in libtbx_refresh.py
    """
    if os.name == "nt" or not stat:  # unsupported
        return
    # Determine the name of the calling module, and thus the internal module name
    # of the libtbx_refresh file. Use exception trick to pick up the current frame.
    try:
        raise Exception()
    except Exception:
        frame = sys.exc_info()[2].tb_frame.f_back
    # Extract the caller name
    caller = frame.f_globals["__name__"]
    if caller == "__main__":
        # well that is not very informative, is it.
        caller = os.path.abspath(
            frame.f_code.co_filename
        )  # Get the full path of the libtbx_refresh.py file.
        refresh_file, _ = os.path.splitext(caller)
        if not refresh_file.endswith("libtbx_refresh"):
            raise RuntimeError(
                "pre-commit nagging can only be done from within libtbx_refresh.py"
            )
        # the name of the parent directory of libtbx_refresh.py is the caller name
        caller = os.path.basename(os.path.dirname(refresh_file))
    else:
        if not caller.endswith(".libtbx_refresh"):
            raise RuntimeError(
                "pre-commit nagging can only be done from within libtbx_refresh.py"
            )
        caller = caller[:-15]

    try:
        import libtbx.load_env
    except Exception as e:
        print("error on importing libtbx environment for pre-commit nagging:", e)
        return
    try:
        path = libtbx.env.dist_path(caller)
    except Exception as e:
        print(f"error on obtaining module path for {caller} for pre-commit nagging:", e)
        return

    if not os.path.isdir(os.path.join(path, ".git")):
        return  # not a developer installation

    precommit_python = abs(libtbx.env.build_path / "precommitbx" / "bin" / "python3")
    hookfile = os.path.join(path, ".git", "hooks", "pre-commit")
    if os.path.isfile(hookfile) and os.access(hookfile, os.X_OK):
        with open(hookfile) as fh:
            precommit = fh.read()
        if "precommitbx" in precommit and os.path.exists(precommit_python):
            return  # legacy libtbx.precommit hook is fine
        if "precommitbx for conda" in precommit:
            return  # libtbx.precommit hook with conda environment is fine
        if "generated by pre-commit" in precommit and "libtbx" not in precommit:
            return  # genuine pre-commit hook is also fine

    try:
        with open(hookfile, "w") as fh:
            fh.write(
                """#!/bin/bash
echo
echo Please install the DIALS pre-commit hooks before committing into the DIALS
echo repository. These hooks run simple static code analysis to catch common
echo coding mistakes early and ensure a common code style.
echo
echo The command you need to run is:
echo "  libtbx.precommit install"
echo

if [ -z "$DIALS_WITHOUT_PRECOMMITS" ]; then
  echo If you want to continue without installing pre-commits then you can override
  echo this check by setting the environment variable DIALS_WITHOUT_PRECOMMITS
fi
echo You can find more information about contributing to DIALS at:
echo https://github.com/dials/dials/blob/master/CONTRIBUTING.md
echo
if [ -z "$DIALS_WITHOUT_PRECOMMITS" ]; then
  exit 1
fi
"""
            )
            mode = os.fstat(fh.fileno()).st_mode
            mode |= stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
            os.fchmod(fh.fileno(), stat.S_IMODE(mode))
    except Exception as e:
        print("Could not generate pre-commit stub:", e)
