import { useState, useRef, useEffect } from 'react'
import { MessageCircle, X, Send, Bot, User, Loader2 } from 'lucide-react'
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { cn } from "@/lib/utils"
import { sendChatMessage, getChatStatus, type ChatMessage } from "@/lib/api"

interface Message extends ChatMessage {
  id: string
  timestamp: Date
}

const SUGGESTED_QUESTIONS = [
  "What is an FCU?",
  "How does adaptive mode work?",
  "Why is Server Room colder?",
  "Energy saving tips?",
]

export function ChatBot() {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isAvailable, setIsAvailable] = useState<boolean | null>(null)
  const [error, setError] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  // Check if chat is available on mount
  useEffect(() => {
    getChatStatus()
      .then(status => setIsAvailable(status.available))
      .catch(() => setIsAvailable(false))
  }, [])

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Focus input when chat opens
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus()
    }
  }, [isOpen])

  const handleSend = async (text?: string) => {
    const messageText = text || input.trim()
    if (!messageText || isLoading) return

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content: messageText,
      timestamp: new Date(),
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)
    setError(null)

    try {
      // Build message history for context
      const history: ChatMessage[] = messages.map(m => ({
        role: m.role,
        content: m.content,
      }))
      history.push({ role: 'user', content: messageText })

      const response = await sendChatMessage(history)

      if (response.error) {
        setError(response.error)
      } else {
        const assistantMessage: Message = {
          id: crypto.randomUUID(),
          role: 'assistant',
          content: response.response,
          timestamp: new Date(),
        }
        setMessages(prev => [...prev, assistantMessage])
      }
    } catch (err) {
      setError('Failed to get response. Please try again.')
      console.error('Chat error:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  // Don't render if chat is not available
  if (isAvailable === false) {
    return null
  }

  return (
    <>
      {/* Floating Button */}
      <Button
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          "fixed bottom-6 right-6 h-14 w-14 rounded-full shadow-lg z-50",
          "bg-zinc-800 hover:bg-zinc-700 border border-zinc-700",
          "transition-transform hover:scale-105",
          isOpen && "rotate-90"
        )}
        size="icon"
      >
        {isOpen ? (
          <X className="h-6 w-6" />
        ) : (
          <MessageCircle className="h-6 w-6" />
        )}
      </Button>

      {/* Chat Window */}
      {isOpen && (
        <Card className={cn(
          "fixed bottom-24 right-6 w-[380px] h-[500px] z-50",
          "flex flex-col shadow-2xl",
          "bg-zinc-900 border-zinc-800",
          "animate-in slide-in-from-bottom-4 fade-in duration-200"
        )}>
          {/* Header */}
          <div className="flex items-center gap-3 px-4 py-3 border-b border-zinc-800">
            <div className="flex items-center justify-center h-8 w-8 rounded-full bg-zinc-800">
              <Bot className="h-4 w-4 text-zinc-400" />
            </div>
            <div>
              <h3 className="font-medium text-sm">FCU Assistant</h3>
              <p className="text-xs text-muted-foreground">Powered by Gemini</p>
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.length === 0 ? (
              <div className="space-y-4">
                <p className="text-sm text-muted-foreground text-center py-4">
                  Ask me anything about your HVAC system!
                </p>
                <div className="space-y-2">
                  <p className="text-xs text-muted-foreground">Suggested questions:</p>
                  {SUGGESTED_QUESTIONS.map((question, i) => (
                    <button
                      key={i}
                      onClick={() => handleSend(question)}
                      className={cn(
                        "block w-full text-left text-sm px-3 py-2 rounded-lg",
                        "bg-zinc-800/50 hover:bg-zinc-800 border border-zinc-800",
                        "transition-colors"
                      )}
                    >
                      {question}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              messages.map((message) => (
                <div
                  key={message.id}
                  className={cn(
                    "flex gap-2",
                    message.role === 'user' && "flex-row-reverse"
                  )}
                >
                  <div className={cn(
                    "flex items-center justify-center h-7 w-7 rounded-full shrink-0",
                    message.role === 'user' ? "bg-zinc-700" : "bg-zinc-800"
                  )}>
                    {message.role === 'user' ? (
                      <User className="h-3.5 w-3.5 text-zinc-400" />
                    ) : (
                      <Bot className="h-3.5 w-3.5 text-zinc-400" />
                    )}
                  </div>
                  <div className={cn(
                    "max-w-[75%] rounded-lg px-3 py-2 text-sm",
                    message.role === 'user'
                      ? "bg-zinc-700 text-zinc-100"
                      : "bg-zinc-800 text-zinc-200"
                  )}>
                    {message.content}
                  </div>
                </div>
              ))
            )}

            {isLoading && (
              <div className="flex gap-2">
                <div className="flex items-center justify-center h-7 w-7 rounded-full bg-zinc-800 shrink-0">
                  <Bot className="h-3.5 w-3.5 text-zinc-400" />
                </div>
                <div className="bg-zinc-800 rounded-lg px-3 py-2">
                  <Loader2 className="h-4 w-4 animate-spin text-zinc-400" />
                </div>
              </div>
            )}

            {error && (
              <div className="text-sm text-red-400 bg-red-950/30 border border-red-900/50 rounded-lg px-3 py-2">
                {error}
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="p-3 border-t border-zinc-800">
            <div className="flex gap-2">
              <input
                ref={inputRef}
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask about FCU controls..."
                disabled={isLoading}
                className={cn(
                  "flex-1 bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2",
                  "text-sm placeholder:text-zinc-500",
                  "focus:outline-none focus:ring-1 focus:ring-zinc-600",
                  "disabled:opacity-50"
                )}
              />
              <Button
                onClick={() => handleSend()}
                disabled={!input.trim() || isLoading}
                size="icon"
                className="bg-zinc-700 hover:bg-zinc-600 shrink-0"
              >
                <Send className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </Card>
      )}
    </>
  )
}
