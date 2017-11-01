for /d %%I in (*) do (
    pushd %%I
    compile * >compile.txt
    popd
)
