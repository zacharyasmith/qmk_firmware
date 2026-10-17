/* Copyright 2023 Brian Low
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */
#include "color.h"
#include "keycodes.h"
#include "keymap_us.h"
#include QMK_KEYBOARD_H

#define GRAVE_MODS  (MOD_BIT(KC_LSFT)|MOD_BIT(KC_RSFT)|MOD_BIT(KC_LGUI)|MOD_BIT(KC_RGUI)|MOD_BIT(KC_LALT)|MOD_BIT(KC_RALT))

// Each layer gets a name for readability.
// The underscores don't mean anything - you can
// have a layer called STUFF or any other name.
// Layer names don't all need to be of the same
// length, and you can also skip them entirely
// and just use numbers.
enum layer_names {
    _BL,
    _L2,
    _L3,
    _MS,
};

const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {
/*
 * Physical layout (sofle_choc): 4x6 main grid per half, one encoder per half
 * on the inner edge of the bottom row, plus a 5-key offset thumb cluster.
 *
 * ,--------------------------------------------.                    ,--------------------------------------------.
 * |  r0c0 |  r0c1 |  r0c2 |  r0c3 |  r0c4 |r0c5|                    |r0c6|  r0c7 |  r0c8 |  r0c9 | r0c10 | r0c11 |
 * |-------+-------+-------+-------+-------+----|                    |----+-------+-------+-------+-------+-------|
 * |  r1c0 |  r1c1 |  r1c2 |  r1c3 |  r1c4 |r1c5|                    |r1c6|  r1c7 |  r1c8 |  r1c9 | r1c10 | r1c11 |
 * |-------+-------+-------+-------+-------+----|                    |----+-------+-------+-------+-------+-------|
 * |  r2c0 |  r2c1 |  r2c2 |  r2c3 |  r2c4 |r2c5|                    |r2c6|  r2c7 |  r2c8 |  r2c9 | r2c10 | r2c11 |
 * |-------+-------+-------+-------+-------+----| ENC_L      ENC_R   |----+-------+-------+-------+-------+-------|
 * |  r3c0 |  r3c1 |  r3c2 |  r3c3 |  r3c4 |r3c5|                    |r3c6|  r3c7 |  r3c8 |  r3c9 | r3c10 | r3c11 |
 * `--------------------------------------------/  T4    \  /   T5   \--------------------------------------------'
 *           |  T0  |  T1  |  T2  |  T3  |      /         \/          \      |  T6  |  T7  |  T8  |  T9  |
 *           `-----------------------------------'          '-----------------------------------------'
 *
 * In the tables below, columns line up with the diagram: the two middle
 * columns are the encoder-row keys (ENC_L / ENC_R), and the last row is the
 * thumb cluster (T0..T4 left, T5..T9 right).
 */

[_BL] = LAYOUT(
    QK_GESC,             KC_1,        KC_2,        KC_3,        KC_4,        KC_5,                         KC_6,       KC_7,        KC_8,        KC_9,        KC_0,           KC_DEL,
    KC_TAB,              KC_Q,        KC_W,        KC_E,        KC_R,        KC_T,                         KC_Y,       KC_U,        KC_I,        KC_O,        KC_P,           _______,
    KC_LCTL,             CTL_T(KC_A), ALT_T(KC_S), SFT_T(KC_D), GUI_T(KC_F), KC_G,                         KC_H,       GUI_T(KC_J), SFT_T(KC_K), ALT_T(KC_L), CTL_T(KC_SCLN), KC_QUOT,
    KC_LSFT,             KC_Z,        KC_X,        KC_C,        KC_V,        KC_B,       KC_MUTE, KC_MPLY, KC_N,       KC_M,        KC_COMM,     KC_DOT,      KC_SLSH,        KC_RSFT,
                                      _______,     KC_TAB,      MO(_L2),     KC_SPC,     KC_PGDN, KC_PGUP, KC_ENT,     MO(_L3),     KC_BSPC,     KC_DEL
),
[_L2] = LAYOUT(
    S(KC_TILD),          S(KC_1),     S(KC_2),     S(KC_3),     S(KC_4),     S(KC_5),                      S(KC_6),    S(KC_7),     S(KC_8),     S(KC_9),     S(KC_0),        KC_PGUP,
    KC_GRAVE,            _______,     KC_UP,       _______,     _______,     S(KC_9),                      S(KC_0),    KC_7,        KC_8,        KC_9,        KC_0,           KC_PGDN,
    _______,             KC_LEFT,     KC_DOWN,     KC_RGHT,     _______,     KC_LBRC,                      KC_RBRC,    KC_4,        KC_5,        KC_6,        KC_PLUS,        KC_PIPE,
    _______,             _______,     _______,     _______,     _______,     S(KC_LBRC), _______, _______, S(KC_RBRC), KC_1,        KC_2,        KC_3,        KC_MINS,        S(KC_PLUS),
                                      _______,     _______,     _______,     _______,    _______, _______, _______,    KC_0,        _______,     _______
),
[_L3] = LAYOUT(
    KC_F12,              KC_F1,       KC_F2,       KC_F3,       KC_F4,       KC_F5,                        KC_F6,      KC_F7,       KC_F8,       KC_F9,       KC_F10,         KC_F11,
    MT(UG_TOGG,LM_TOGG), S(KC_1),     S(KC_2),     S(KC_3),     S(KC_4),     S(KC_5),                      S(KC_6),    S(KC_7),     S(KC_8),     S(KC_9),     S(KC_0),        KC_PGUP,
    MT(UG_NEXT,LM_NEXT), KC_MPRV,     KC_MNXT,     KC_VOLU,     KC_PGUP,     S(KC_MINS),                   S(KC_PLUS), _______,     _______,     _______,     _______,        _______,
    _______,             _______,     _______,     KC_VOLD,     KC_PGDN,     KC_MINS,    _______, _______, KC_PLUS,    _______,     _______,     _______,     _______,        KC_BSLS,
                                      _______,     TG(_MS),     TG(_MS),     _______,    _______, _______, _______,    _______,     _______,     _______
),
[_MS] = LAYOUT(
    _______,             _______,     _______,     _______,     _______,     _______,                      _______,    _______,     _______,     _______,     _______,        _______,
    _______,             _______,     _______,     _______,     _______,     _______,                      _______,    MS_WHLD,     MS_UP,       MS_WHLU,     _______,        _______,
    _______,             MS_BTN1,     MS_BTN2,     MS_BTN3,     MS_BTN4,     MS_BTN5,                      MS_WHLL,    MS_LEFT,     MS_DOWN,     MS_RGHT,     MS_WHLR,        _______,
    _______,             _______,     _______,     _______,     _______,     _______,    _______, _______, _______,    _______,     _______,     _______,     _______,        _______,
                                      _______,     TG(_MS),     MS_ACL0,     _______,    _______, _______, _______,    TG(_MS),     _______,     _______
)
};

#if defined(ENCODER_MAP_ENABLE)
#define COMMON_ENCODER_MAPPING { ENCODER_CCW_CW(KC_VOLU, KC_VOLD), ENCODER_CCW_CW(KC_MNXT, KC_MPRV) }
const uint16_t PROGMEM encoder_map[][NUM_ENCODERS][NUM_DIRECTIONS] = {
    [_BL] = COMMON_ENCODER_MAPPING,
    [_L2] = COMMON_ENCODER_MAPPING,
    [_L3] = COMMON_ENCODER_MAPPING,
    [_MS] = { ENCODER_CCW_CW(MS_WHLD, MS_WHLU), ENCODER_CCW_CW(MS_WHLL, MS_WHLR) }
};
#endif
