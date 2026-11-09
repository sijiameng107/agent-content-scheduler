#!/bin/zsh
set -eu
cd "${0:A:h:h}"
if [[ -z "${ZHIPU_API_KEY:-}" ]]; then
  if [[ -n "${OPENROUTER_API_KEY:-}" ]]; then
    print '将当前终端原先保存在 OPENROUTER_API_KEY 的智谱密钥用于本次运行。'
    export ZHIPU_API_KEY="$OPENROUTER_API_KEY"
  else
    read -r -s 'ZHIPU_API_KEY?粘贴智谱普通 API Key 后按回车（不显示）：'
    print
    export ZHIPU_API_KEY
  fi
fi
export ZHIPU_MODEL="${ZHIPU_MODEL:-glm-4-flash-250414}"
run_folder="examples/live-$(date +%Y%m%d-%H%M%S)"
print "运行智谱验收；证据将保存到 $run_folder"
python3 scripts/evaluate.py --mode live --output "$run_folder"
