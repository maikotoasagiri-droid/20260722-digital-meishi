import json
import sys
from pathlib import Path

import qrcode
from qrcode.constants import ERROR_CORRECT_H

BASE_DIR = Path(__file__).resolve().parent
PROFILE_PATH = BASE_DIR / "profile.json"
OUTPUT_PATH = BASE_DIR / "output" / "meishi_qr.png"
VCARD_PATH = BASE_DIR / "output" / "meishi.vcf"
MAX_VCARD_BYTES = 500


def load_profile(path):
    if not path.exists():
        print(f"エラー: {path.name} が見つかりません")
        sys.exit(1)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"エラー: {path.name} のJSON読み込みに失敗しました: {e}")
        sys.exit(1)


def build_vcard(profile):
    name = profile.get("name", "").strip()
    name_kana = profile.get("name_kana", "").strip()
    org = profile.get("org", "").strip()
    title = profile.get("title", "").strip()
    title2 = profile.get("title2", "").strip()
    tel = profile.get("tel", "").strip()
    tel_work = profile.get("tel_work", "").strip()
    email = profile.get("email", "").strip()
    url = profile.get("url", "").strip()
    line_id = profile.get("line_id", "").strip()
    instagram_id = profile.get("instagram_id", "").strip()

    lines = ["BEGIN:VCARD", "VERSION:3.0"]

    parts = name.split()
    if len(parts) == 2:
        sei, mei = parts
        lines.append(f"N:{sei};{mei};;;")

        kana_parts = name_kana.split()
        if len(kana_parts) == 2:
            sei_kana, mei_kana = kana_parts
            lines.append(f"X-PHONETIC-LAST-NAME:{sei_kana}")
            lines.append(f"X-PHONETIC-FIRST-NAME:{mei_kana}")

        lines.append(f"FN:{sei} {mei}")
    else:
        lines.append(f"FN:{name}")

    if org:
        lines.append(f"ORG:{org}")

    if title and title2:
        lines.append(f"TITLE:{title}／{title2}")
    elif title:
        lines.append(f"TITLE:{title}")
    elif title2:
        lines.append(f"TITLE:{title2}")

    if tel:
        lines.append(f"TEL;TYPE=CELL:{tel}")
    if tel_work:
        lines.append(f"TEL;TYPE=WORK:{tel_work}")

    if email:
        lines.append(f"EMAIL:{email}")
    if url:
        lines.append(f"URL:{url}")

    note_parts = []
    if line_id:
        note_parts.append(f"LINE ID: {line_id}")
    if instagram_id:
        note_parts.append(f"Instagram: {instagram_id}")
    if note_parts:
        lines.append("NOTE:" + "\\n".join(note_parts))

    lines.append("END:VCARD")
    return "\r\n".join(lines)


def main():
    profile = load_profile(PROFILE_PATH)

    name = profile.get("name", "").strip()
    tel = profile.get("tel", "").strip()
    tel_work = profile.get("tel_work", "").strip()
    email = profile.get("email", "").strip()

    if not name and not tel and not tel_work and not email:
        print("氏名と連絡先（携帯電話・勤務先電話・メールのいずれか）は必須です")
        sys.exit(1)

    vcard = build_vcard(profile)

    vcard_bytes = len(vcard.encode("utf-8"))
    if vcard_bytes > MAX_VCARD_BYTES:
        print(
            f"vCardが{MAX_VCARD_BYTES}文字制限を超えています（現在{vcard_bytes}文字）。"
            "urlやtitle2、NOTEの内容などの削減を検討してください"
        )
        sys.exit(1)

    qr = qrcode.QRCode(error_correction=ERROR_CORRECT_H)
    qr.add_data(vcard)
    qr.make(fit=True)
    img = qr.make_image()

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUTPUT_PATH)

    with open(VCARD_PATH, "w", encoding="utf-8", newline="") as f:
        f.write(vcard + "\r\n")

    print(f"生成完了: output/meishi_qr.png（vCard文字数: {len(vcard)}文字）")
    print("　　　　　 output/meishi.vcf（フリガナ込み・直接送付用）")


if __name__ == "__main__":
    main()
