#!/bin/sh
# Host-side Docker adapter for the frozen COMPAT-001A harness.
# Dedicated synthetic lab only; existing development containers are untouched.
set -eu
LAB=/home/berpadmin/berp-mfi-compat-r1
BENCH_IMAGE=frappe/bench@sha256:2132ebefed475ab4b898e0847fe00e1a8f50413dc528aafdecd188428e21b0a6
cd "$LAB"
sha256sum -c <<'SUMS'
217d4e48043770ac3cc44ce7001107f162ed1580cbfffca9c73bf2c83a0275d9  sources/frappe.tar.gz
374957165ae8d784f6ebdd30414b47077a5a5e9519d48bf61703b577f45533b0  sources/erpnext.tar.gz
888e2bf910b00a2cefc4aeb220a6ab7162710a3a582a5de838252a81998acb0e  sources/lending.tar.gz
SUMS
test ! -d bench
{
  date -u +%FT%TZ
  uname -srmo
  . /etc/os-release
  printf 'host_os=%s\n' "$PRETTY_NAME"
  stat -f -c 'filesystem=%T' .
  sudo -n docker info --format 'runtime={{.ServerVersion}} cgroups={{.CgroupVersion}}'
  printf 'frozen_harness=9a47f56f5bfda3249a2aa898f18e9e4adb245711\n'
  sha256sum harness/*
} > evidence/host.txt
sudo -n docker create --name mfi-r1-builder --memory=1g --memory-swap=1g --cpus=1 \
  -v "$LAB:/workspace" -v "$LAB/harness:/harness:ro" "$BENCH_IMAGE" \
  sh -c 'date -u +%FT%TZ > /workspace/evidence/prepare.started; timeout --kill-after=15 1200 sh /harness/prepare-lab.sh > /workspace/evidence/prepare.log 2>&1; rc=$?; printf "%s\n" "$rc" > /workspace/evidence/prepare.exit; date -u +%FT%TZ > /workspace/evidence/prepare.finished; exit "$rc"'
sudo -n docker start mfi-r1-builder
