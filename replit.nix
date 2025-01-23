{ pkgs }: {
  deps = [
    pkgs.redis
    pkgs.python3
    pkgs.python3Packages.redis
  ];
}