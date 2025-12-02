
import os, wave, array

def extract_bank(path, outdir_prefix=""):
    with open(path, "rb") as f:
        buf = f.read()

    sample_tag = b'\x36\x31\x35\x30\x53\x6D\x70\x44'
    sample_indices = []
    loc = 0
    while True:
        sample_n = buf.find(sample_tag, loc)
        if sample_n < 0:
            break
        sample_indices.append(sample_n)
        loc = sample_n + 1

    base = os.path.basename(path)
    if base.lower().endswith(".msmpl_bank"):
        base_noext = base[:-11]
    else:
        base_noext = base
    parts = [p.strip() for p in base_noext.split('-')]
    bank_prefix = parts[-1] if parts else base_noext

    extracted = []
    sample_c = 0

    for sample_n in sample_indices:
        name = buf[sample_n+32:sample_n+40].decode("utf-8", errors="replace").strip()
        wav_len = int.from_bytes(buf[sample_n+96:sample_n+99], "little")
        fmt = buf[sample_n+102]

        if wav_len == 0:
            continue

        if fmt & 0x01 == 1:
            ch = 2
        else:
            ch = 1

        sr_code = (fmt & 0x0C) >> 2
        if   sr_code == 0: sr = 48000
        elif sr_code == 1: sr = 24000
        elif sr_code == 2: sr = 12000
        elif sr_code == 3: sr = 6000
        else: sr = 48000

        data_buf = bytearray(buf[sample_n+96:sample_n+96+wav_len])
        if len(data_buf) % 2 != 0:
            data_buf = data_buf[:-1]
        data_buf[0::2], data_buf[1::2] = data_buf[1::2], data_buf[0::2]

        sample_c += 1
        safe_name = name if name else f"SMPL{sample_c:02}"
        wav_fn = f"{bank_prefix}_{sample_c:02}_{safe_name}.wav"
        out_path = os.path.join(outdir_prefix, wav_fn)

        with wave.open(out_path, "wb") as wf:
            wf.setnchannels(ch)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            wf.writeframes(data_buf)

        extracted.append(out_path)

    return extracted
