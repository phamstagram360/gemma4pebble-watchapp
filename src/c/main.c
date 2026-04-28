#include <pebble.h>

// Message keys must match iOS app Constants.swift
#define KEY_CHAT      0
#define KEY_PROMPT    2
#define KEY_CHAT_DONE 7
#define KEY_WARNING   32

static Window         *s_window;
static TextLayer      *s_status_layer;
static TextLayer      *s_response_layer;
static DictationSession *s_dictation_session;
static char            s_response_buf[512];

// ── Dictation ────────────────────────────────────────────────────────────────

static void dictation_callback(DictationSession *session,
                               DictationSessionStatus status,
                               char *transcription,
                               void *context) {
  if (status == DictationSessionStatusSuccess) {
    text_layer_set_text(s_status_layer, "Thinking...");
    text_layer_set_text(s_response_layer, "");

    DictionaryIterator *iter;
    if (app_message_outbox_begin(&iter) == APP_MSG_OK) {
      dict_write_cstring(iter, KEY_PROMPT, transcription);
      app_message_outbox_send();
    }
  } else {
    text_layer_set_text(s_status_layer, "Press \xe2\x96\xb6 to ask");
  }
}

// ── AppMessage inbox ─────────────────────────────────────────────────────────

static void inbox_received(DictionaryIterator *iter, void *context) {
  Tuple *chat_t    = dict_find(iter, KEY_CHAT);
  Tuple *done_t    = dict_find(iter, KEY_CHAT_DONE);
  Tuple *warning_t = dict_find(iter, KEY_WARNING);

  if (chat_t && chat_t->type == TUPLE_CSTRING) {
    strncpy(s_response_buf, chat_t->value->cstring, sizeof(s_response_buf) - 1);
    text_layer_set_text(s_response_layer, s_response_buf);
  }
  if (done_t) {
    text_layer_set_text(s_status_layer, "Press \xe2\x96\xb6 to ask");
  }
  if (warning_t && warning_t->type == TUPLE_CSTRING) {
    text_layer_set_text(s_status_layer, warning_t->value->cstring);
  }
}

static void inbox_dropped(AppMessageResult reason, void *context) {
  APP_LOG(APP_LOG_LEVEL_ERROR, "Inbox dropped: %d", (int)reason);
}

// ── Clicks ───────────────────────────────────────────────────────────────────

static void select_click(ClickRecognizerRef recognizer, void *context) {
  dictation_session_start(s_dictation_session);
}

static void click_config_provider(void *context) {
  window_single_click_subscribe(BUTTON_ID_SELECT, select_click);
}

// ── Window ───────────────────────────────────────────────────────────────────

static void window_load(Window *window) {
  Layer  *root   = window_get_root_layer(window);
  GRect   bounds = layer_get_bounds(root);

  // Status bar at top
  s_status_layer = text_layer_create(GRect(0, 4, bounds.size.w, 24));
  text_layer_set_text(s_status_layer, "Press \xe2\x96\xb6 to ask");
  text_layer_set_text_alignment(s_status_layer, GTextAlignmentCenter);
  text_layer_set_font(s_status_layer, fonts_get_system_font(FONT_KEY_GOTHIC_14));
  layer_add_child(root, text_layer_get_layer(s_status_layer));

  // Divider line
  Layer *line = layer_create(GRect(0, 28, bounds.size.w, 2));
  layer_add_child(root, line);

  // Response area
  s_response_layer = text_layer_create(
    GRect(4, 32, bounds.size.w - 8, bounds.size.h - 36));
  text_layer_set_text(s_response_layer, "AI Assistant\nfor Pebble\n\nPress the middle\nbutton and ask\nanything.");
  text_layer_set_text_alignment(s_response_layer, GTextAlignmentLeft);
  text_layer_set_font(s_response_layer,
    fonts_get_system_font(FONT_KEY_GOTHIC_18_BOLD));
  text_layer_set_overflow_mode(s_response_layer, GTextOverflowModeWordWrap);
  layer_add_child(root, text_layer_get_layer(s_response_layer));
}

static void window_unload(Window *window) {
  text_layer_destroy(s_status_layer);
  text_layer_destroy(s_response_layer);
}

// ── App lifecycle ─────────────────────────────────────────────────────────────

static void init(void) {
  app_message_register_inbox_received(inbox_received);
  app_message_register_inbox_dropped(inbox_dropped);
  app_message_open(2048, 256);

  s_dictation_session = dictation_session_create(512, dictation_callback, NULL);

  s_window = window_create();
  window_set_click_config_provider(s_window, click_config_provider);
  window_set_window_handlers(s_window, (WindowHandlers){
    .load   = window_load,
    .unload = window_unload,
  });
  window_stack_push(s_window, true);
}

static void deinit(void) {
  dictation_session_destroy(s_dictation_session);
  window_destroy(s_window);
}

int main(void) {
  init();
  app_event_loop();
  deinit();
}
