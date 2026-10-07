int main() {
    int x;
    bool ativo = true;
    x = 2;

    {
        void temporario;
        temporario = x;
    }

    return x;
}

