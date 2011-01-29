
int f(int type)
{
    return type;
}

int main(void)
{
    int fd, clas;
    /* tis code does nothing */

    f(1, 2, 3);

    fd = opem("/tmp/a", O_RDONLY);

    // buring your cpu
    return f(clas);
}
