# Tools for working with travis-ci
WHEELHOSTS="travis-wheels.scikit-image.org travis-dev-wheels.scipy.org"

PIP_FLAGS="--timeout=60 --no-index"

for host in $WHEELHOSTS; do
   PIP_FLAGS="${PIP_FLAGS} --trusted-host ${host} --find-links=http://${host}"
done


retry () {
    # https://gist.github.com/fungusakafungus/1026804
    local retry_max=5
    local count=$retry_max
    while [ $count -gt 0 ]; do
        "$@" && break
        count=$(($count - 1))
        sleep 1
    done

    [ $count -eq 0 ] && {
        echo "Retry failed [$retry_max]: $@" >&2
        return 1
    }
    return 0
}


wheelhouse_pip_install() {
    # Install pip requirements via travis wheelhouse
    retry pip install $PIP_FLAGS $@
}
