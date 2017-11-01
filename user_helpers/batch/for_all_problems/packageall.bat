rmdir /s _packages
for /d %%I in (*) do (
    pushd %%I
    package
    popd
)
