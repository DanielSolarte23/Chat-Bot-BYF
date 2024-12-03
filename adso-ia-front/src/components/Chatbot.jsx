import React, { useState } from "react";

const Chatbot = () => {
  const [userMessage, setUserMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false); // Para el indicador de carga

  // Función para limpiar y procesar el texto
  const preprocessMessage = (message) => {
    return message
      .toLowerCase() // Convertir a minúsculas
      .replace(/[^\w\s]/gi, "") // Eliminar caracteres especiales
      .replace(/\s+/g, " ") // Eliminar espacios múltiples
      .trim(); // Quitar espacios al inicio y al final
  };

  // Función para limpiar la respuesta del bot (opcional)
  const preprocessBotResponse = (response) => {
    return response
    //   .replace(/[^\w\s.,!?]/gi, "") // Eliminar caracteres no alfabéticos o especiales innecesarios
      .trim(); // Limpiar espacios innecesarios
  };

  // Función para manejar el envío de mensajes
  const handleSendMessage = async () => {
    if (userMessage.trim() === "") return;

    // Preprocesar el mensaje antes de enviarlo
    const cleanedMessage = preprocessMessage(userMessage);

    const newMessage = { sender: "user", text: userMessage };
    setMessages((prevMessages) => [...prevMessages, newMessage]);
    setUserMessage("");
    setIsLoading(true); // Mostrar indicador de carga

    // Enviar mensaje a la API y obtener la respuesta
    try {
      const response = await fetch("http://127.0.0.1:5000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json; charset=utf-8",
        },
        body: JSON.stringify({ message: cleanedMessage }), // Enviar mensaje procesado
      });
      const data = await response.json();

      // Preprocesar la respuesta del bot
      const botMessage = { sender: "bot", text: preprocessBotResponse(data.response) };

      // Actualizar mensajes con la respuesta del bot
      setMessages((prevMessages) => [...prevMessages, botMessage]);
    } catch (error) {
      console.error("Error al comunicarse con la API", error);
      setMessages((prevMessages) => [
        ...prevMessages,
        { sender: "bot", text: "Lo siento, ocurrió un error. Intenta de nuevo más tarde." }
      ]);
    } finally {
      setIsLoading(false); // Ocultar indicador de carga
    }
  };

  return (
    <div className="w-full max-w-lg p-4 bg-zinc-900 border rounded-lg shadow-lg">
      <div className="h-96 overflow-y-auto border-b-2 border-gray-200 p-4 mb-4">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`${
              msg.sender === "user" ? "text-right" : "text-left"
            } mb-2`}
          >
            <div
              className={`inline-block p-2 rounded-lg ${
                msg.sender === "user" ? "bg-blue-500 text-white" : "bg-gray-200"
              }`}
            >
              {msg.text}
            </div>
          </div>
        ))}
        {/* Mostrar indicador de carga */}
        {isLoading && (
          <div className="text-center text-gray-500">Cargando...</div>
        )}
      </div>
      <div className="flex">
        <input
          type="text"
          value={userMessage}
          onChange={(e) => setUserMessage(e.target.value)}
          placeholder="Escribe un mensaje..."
          className="w-full p-2 border border-gray-300 rounded-l-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          onClick={handleSendMessage}
          className="p-2 bg-blue-500 text-white rounded-r-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          Enviar
        </button>
      </div>
    </div>
  );
};

export default Chatbot;
