from modules.chat_manager import ChatManager


def test_create_and_list_conversation(tmp_path):
    chat = ChatManager(tmp_path / "chat.db")
    conversation_id = chat.new_conversation("Research")
    conversations = chat.list_conversations()
    assert conversations[0]["id"] == conversation_id
    assert chat.count() == 1


def test_rename_delete_conversation(tmp_path):
    chat = ChatManager(tmp_path / "chat.db")
    conversation_id = chat.new_conversation("Old title")
    chat.add_message(conversation_id, "user", "Hello")
    chat.rename_conversation(conversation_id, "New title")
    assert chat.list_conversations()[0]["title"] == "New title"
    assert chat.get_messages(conversation_id)[0]["content"] == "Hello"
    chat.delete_conversation(conversation_id)
    assert chat.count() == 0
