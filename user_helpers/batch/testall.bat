for /d %%I in (*) do (
    pushd %%I
    testsol * -t5 -m512 >testsol.txt
    popd
)
