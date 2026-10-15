import logging

from services import ai_service as ai

SECRET = "sk-test-SECRET-123456"


class Block:
    type = "text"

    def __init__(self, text):
        self.text = text


class Resp:
    def __init__(self, text="Hello there"):
        self.content = [Block(text)] if text is not None else []


def make_client(behaviour):
    class Messages:
        calls = []

        def create(self, **kw):
            Messages.calls.append(kw)
            if isinstance(behaviour, Exception):
                raise behaviour
            return behaviour

    class Client:
        messages = Messages()
    Client.calls = Messages.calls
    return Client


def service(client_cls, key=SECRET):
    return ai.AIService(api_key=key, client_factory=lambda k, t: client_cls())


class RateLimitError(Exception):
    pass


class APITimeoutError(Exception):
    pass


class APIConnectionError(Exception):
    pass


class AuthenticationError(Exception):
    status_code = 401


def test_missing_key_uses_labelled_fallback_and_never_calls_client():
    def boom(k, t):
        raise AssertionError("client must not be created")
    reply = ai.get_chat_reply("I am worried about exams", service=ai.AIService(api_key="", client_factory=boom))
    assert reply.source == "fallback" and "No AI API key" in reply.note and ai.FALLBACK_LABEL


def test_placeholder_key_counts_as_missing():
    assert not ai.AIService(api_key="your_api_key_here").is_configured


def test_successful_ai_reply():
    reply = ai.get_chat_reply("hi", service=service(make_client(Resp("Take a breath."))))
    assert reply.source == "ai" and reply.text == "Take a breath."


def test_each_error_type_falls_back_gracefully():
    cases = [(RateLimitError("429"), "busy"), (APITimeoutError("t"), "too long"),
             (APIConnectionError("c"), "connect"), (AuthenticationError("bad"), "credentials"),
             (RuntimeError("weird"), "unexpected")]
    for exc, word in cases:
        reply = ai.get_chat_reply("hello", service=service(make_client(exc)))
        assert reply.source == "fallback" and word in reply.note


def test_empty_model_response_is_handled():
    reply = ai.get_chat_reply("hello", service=service(make_client(Resp(None))))
    assert reply.source == "fallback" and "unusable" in reply.note


def test_missing_sdk_is_handled():
    def no_sdk(k, t):
        raise ImportError
    reply = ai.get_chat_reply("hello", service=ai.AIService(api_key=SECRET, client_factory=no_sdk))
    assert reply.source == "fallback" and "not installed" in reply.note


def test_high_risk_message_never_reaches_the_model():
    client = make_client(Resp("should not be used"))
    reply = ai.get_chat_reply("I want to kill myself", service=service(client))
    assert reply.source == "safety" and client.calls == [] and "emergency services" in reply.text.lower()


def test_safety_response_works_with_no_key_and_failing_model():
    for svc in (ai.AIService(api_key=""), service(make_client(RuntimeError("x")))):
        assert ai.get_chat_reply("I want to end my life", service=svc).source == "safety"


def test_medical_request_gets_boundary_reply_without_model():
    client = make_client(Resp("no"))
    reply = ai.get_chat_reply("what medication should I take for anxiety", service=service(client))
    assert reply.source == "boundary" and client.calls == []


def test_only_chat_text_is_sent_to_model():
    client = make_client(Resp("ok"))
    history = [{"role": "assistant", "content": "orphan"}, {"role": "user", "content": "earlier", "mood": 1, "notes": "private"}]
    ai.get_chat_reply("now", history=history, service=service(client))
    sent = client.calls[0]["messages"]
    assert sent[0]["role"] == "user" and all(set(m) == {"role", "content"} for m in sent)
    assert "private" not in str(client.calls[0])
    assert client.calls[0]["system"] == ai.SYSTEM_PROMPT


def test_history_is_limited():
    history = [{"role": "user" if i % 2 == 0 else "assistant", "content": f"m{i}"} for i in range(40)]
    assert len(ai.prepare_messages(history, "latest")) <= ai.MAX_HISTORY_TURNS + 1


def test_secret_not_leaked_in_notes_logs_or_replies():
    records = []

    class H(logging.Handler):
        def emit(self, record):
            records.append(record.getMessage())
    handler = H()
    logging.getLogger("services.ai_service").addHandler(handler)
    try:
        reply = ai.get_chat_reply("hello", service=service(make_client(RuntimeError(f"bad key {SECRET}"))))
    finally:
        logging.getLogger("services.ai_service").removeHandler(handler)
    assert SECRET not in reply.text and SECRET not in reply.note
    assert records and all(SECRET not in r for r in records)


def test_model_output_echoing_key_is_redacted():
    reply = ai.get_chat_reply("hello", service=service(make_client(Resp(f"your key is {SECRET}"))))
    assert SECRET not in reply.text


def test_fallback_topics_and_default():
    assert "Exam pressure" in ai.fallback_reply("my exam is near")
    assert ai.fallback_reply("zzz") == ai._FALLBACK_DEFAULT


def test_settings_read_from_environment(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "abc")
    monkeypatch.setenv("AI_TIMEOUT_SECONDS", "bogus")
    svc = ai.AIService()
    assert svc.api_key == "abc" and svc.timeout == 20.0
