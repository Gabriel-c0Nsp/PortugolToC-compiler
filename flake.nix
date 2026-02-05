
{
  description = "Projeto final da cadeira de Teoria Da Computação e Compiladores";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };
      python = pkgs.python3;
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        packages = [
          (python.withPackages (ps: with ps; [
          # pacotes e dependências adicionais devem vir aqui...
          ]))
        ];
      };
    };
}
