

int main(void)
{
    int fd;
    /* tis code does nothing */

    f(1, 2, 3);

    fd = opem("/tmp/a", O_RDONLY);
    return 0;
}
