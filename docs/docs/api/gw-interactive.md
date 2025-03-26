

---
layout: default
title: Interactivity
parent: API Reference
nav_order: 7
---

# Interactive Controls
{: .no_toc }

- TOC
{:toc}

---

## apply_command
`apply_command(command)`

Apply a GW command string.

**Parameters:**
- `command` (str): GW command to execute (e.g., "filter", "count", etc.)

---

## key_press
`key_press(key, scancode, action, mods)`

Process a key press event.

**Parameters:**
- `key` (int): Key code
- `scancode` (int): Scan code
- `action` (int): Key action code
- `mods` (int): Modifier keys

---

## mouse_event
`mouse_event(x_pos, y_pos, button, action)`

Process a mouse event.

**Parameters:**
- `x_pos` (float): Mouse x-position
- `y_pos` (float): Mouse y-position
- `button` (int): Mouse button code
- `action` (int): Mouse action code

---

