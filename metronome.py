"""metronome - 终端节拍器。纯标准库。

用法：python -m metronome 120 [--beats 4] [--duration 30s] [--no-bell]
"""

import argparse
import sys
import time


def parse_bpm(value: str) -> int:
    """解析 BPM。返回整数 BPM，无效则抛 ValueError。"""
    try:
        bpm = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"无效的速度：{value}（BPM 必须是 1-400 的整数）")
    if not 1 <= bpm <= 400:
        raise ValueError(f"无效的速度：{bpm}（BPM 必须是 1-400 的整数）")
    return bpm


def parse_duration(value: str) -> float:
    """解析时长："30s"/"90"/"2m"/"1h" -> 秒。"""
    value = value.strip().lower()
    try:
        if value.endswith("h"):
            return float(value[:-1]) * 3600
        if value.endswith("m"):
            return float(value[:-1]) * 60
        if value.endswith("s"):
            value = value[:-1]
        secs = float(value)
    except ValueError:
        raise ValueError(f"无法解析时长：{value}（如 30s / 2m / 1h）")
    if secs <= 0:
        raise ValueError(f"时长必须大于 0：{value}")
    return secs


def run(bpm: int, beats: int, duration: float | None, use_bell: bool) -> int:
    """主循环。返回敲击次数。"""
    interval = 60.0 / bpm
    total = 0
    start = time.monotonic()
    deadline = start + duration if duration is not None else None
    print(f"节拍器：{bpm} BPM，每小节 {beats} 拍。按 Ctrl-C 停止。", flush=True)
    try:
        while True:
            beat_index = total % beats
            strong = beat_index == 0
            now = time.monotonic()
            if deadline is not None and now >= deadline:
                break
            marker = "🔔" if strong else "·"
            bar = "█" * (beat_index + 1) + "░" * (beats - beat_index - 1)
            line = f"\r{marker} 第 {total + 1} 拍 [{bar}]"
            sys.stdout.write(line)
            sys.stdout.flush()
            if use_bell:
                # 强拍双响以示重音
                sys.stdout.write("\a" + ("\a" if strong else ""))
                sys.stdout.flush()
            total += 1
            # 以 monotonic 为基准规划下一次敲击，避免累积漂移
            target = start + total * interval
            delay = target - time.monotonic()
            if delay > 0:
                time.sleep(delay)
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write("\n")
    elapsed = time.monotonic() - start
    print(f"停止。共敲击 {total} 拍，用时 {elapsed:.1f} 秒。")
    return total


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="metronome",
        description="终端节拍器：按指定速度打拍子（纯标准库）。",
    )
    parser.add_argument("bpm", help="速度，如 120（BPM，1-400）")
    parser.add_argument("--beats", type=int, default=4,
                        help="每小节拍数，首拍为重音（默认 4）")
    parser.add_argument("--duration", default=None,
                        help="运行时长，如 30s / 2m，到时自动停止")
    parser.add_argument("--no-bell", action="store_true",
                        help="只显示不响铃")
    args = parser.parse_args(argv)

    try:
        bpm = parse_bpm(args.bpm)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    if not 1 <= args.beats <= 12:
        print("error: --beats 必须是 1-12 的整数", file=sys.stderr)
        return 1
    duration = None
    if args.duration is not None:
        try:
            duration = parse_duration(args.duration)
        except ValueError as e:
            print(f"error: {e}", file=sys.stderr)
            return 1
    run(bpm, args.beats, duration, use_bell=not args.no_bell)
    return 0


if __name__ == "__main__":
    sys.exit(main())
