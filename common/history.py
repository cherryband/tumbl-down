#!/usr/bin/python
from __future__ import annotations
from typing import Optional
import dataclasses


@dataclasses.dataclass
class History:
    service: str
    account: str
    post_id: str
    timestamp: str

@dataclasses.dataclass
class Post:
    post_id: str
    timestamp: int

def _write_line(writer, line: str, line_no: Optional[int] = None) -> None:
    writer.seek(0)
    lines = writer.readlines()
    if not lines:
        lines = []

    if line_no is not None:
        lines[line_no] = f"{line}\n"
    else:
        lines.append(f"{line}\n")

    writer.seek(0)
    writer.writelines(lines)

def _write_history(writer, history: History, line_no: Optional[int] = None) -> None:
    _write_line(writer, f"{history.service}, {history.account}, "
                f"{history.post_id}, {history.timestamp}", line_no)

def mark_read(rwriter, history: History) -> bool:
    last_pos = None
    last_read = None

    if val:=get_last_read(rwriter, history.service, history.account, True):
        last_read, last_pos = val

    if last_read and last_read.timestamp > int(history.timestamp):
        return False
    _write_history(rwriter, history, last_pos)
    return True

def get_last_read(reader, service, account, _line_no: bool = False) \
                 -> Optional[tuple[Post, Optional[int]]]:
    reader.seek(0)

    for i, line in enumerate(reader):
        row = [item.strip() for item in line.split(',')]
        if row[0] == service and row[1] == account:
            return (Post(row[2], int(row[3])), i) if _line_no else Post(row[2], int(row[3]))
    return None
