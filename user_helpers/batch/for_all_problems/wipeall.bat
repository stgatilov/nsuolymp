for /d %%I in (*) do (
    pushd %%I
    wipe -ic -q >wipe.txt
    popd
)
