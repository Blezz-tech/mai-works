{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    (pkgs.python313.withPackages (python-pkgs: [
      python-pkgs.pandas
      python-pkgs.pyqt6
    ]))
  ];

  # Опционально можно настроить переменную окружения, чтобы PyQt корректно работал
  # с вашим окружением, например:
  # shellHook = ''
  #   export QT_QPA_PLATFORM=wayland
  # '';
}
