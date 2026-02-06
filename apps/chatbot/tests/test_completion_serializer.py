from django.test import TestCase

from apps.chatbot.serializers.completion import ChatbotCompletionCreateSerializer


class ChatbotCompletionSerializerTest(TestCase):
    def test_valid_message(self) -> None:
        serializer = ChatbotCompletionCreateSerializer(data={"message": "hi"})
        self.assertTrue(serializer.is_valid())

    def test_blank_message(self) -> None:
        serializer = ChatbotCompletionCreateSerializer(data={"message": ""})
        self.assertFalse(serializer.is_valid())
