import random
import re

class CipherBot:
    def __init__(self, user_data, api_key=None):
        self.user_data = user_data
        self.api_key = api_key
        
        # Initialize Hugging Face client if API key is provided
        if self.api_key:
            try:
                from huggingface_hub import InferenceClient
                self.client = InferenceClient(token=self.api_key)
                self.use_ai = True
                print("🤖 AI mode enabled")
            except Exception as e:
                print(f"⚠️  Failed to initialize AI: {e}")
                self.client = None
                self.use_ai = False
        else:
            self.client = None
            self.use_ai = False
            print("📝 Basic mode enabled (no AI)")
        
        self.fun_facts = [
            "Did you know? Honey never spoils. Archaeologists have found 3000-year-old honey in Egyptian tombs that's still edible!",
            "Fun fact: Octopuses have three hearts and blue blood. Two hearts pump blood to the gills, one to the rest of the body!",
            "Here's something cool: Bananas are berries, but strawberries aren't. Botany is wild, right?",
            "Random knowledge drop: A day on Venus is longer than its year. It takes 243 Earth days to rotate once!",
            "Educational tidbit: Your brain uses about 20% of your body's energy, despite being only 2% of your body weight.",
            "Neat fact: Butterflies can taste with their feet. Imagine that being your superpower!",
            "Did you know? The shortest war in history lasted 38 minutes between Britain and Zanzibar in 1896.",
            "Science time: Water can boil and freeze at the same time. It's called the triple point!",
            "Fun learning: Dolphins have names for each other and call out to specific dolphins.",
            "Cool info: A group of flamingos is called a 'flamboyance'. Fitting, isn't it?"
        ]
        
        # Conversation history for context
        self.conversation_history = []
    
    def get_greeting(self):
        if self.user_data['name']:
            return f"Hey {self.user_data['name']}! Back for more of my sparkling personality? I've missed our chats. 😏"
        else:
            return "Well, well, well... A new human! I'm Cipher, your friendly neighborhood sarcastic robot. What should I call you?"
    
    def extract_info(self, text):
        updated = False
        
        # Extract name
        if not self.user_data['name']:
            name_patterns = [
                r"(?:my name is|i'm|i am|call me) ([a-zA-Z]+)",
                r"^([a-zA-Z]+)$"
            ]
            for pattern in name_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match and len(match.group(1)) > 1 and len(match.group(1)) < 20:
                    self.user_data['name'] = match.group(1).capitalize()
                    updated = True
                    break
        
        # Extract interests
        interest_patterns = [
            r"i (?:love|like|enjoy|am into) ([^.!?]+)",
            r"my (?:hobby|hobbies|interest|interests) (?:is|are|include) ([^.!?]+)"
        ]
        for pattern in interest_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                interest = match.group(1).strip()
                if interest not in self.user_data['interests'] and len(interest) < 50:
                    self.user_data['interests'].append(interest)
                    updated = True
        
        # Extract facts
        fact_patterns = [
            r"i (?:work|study|live) (?:as|in|at) ([^.!?]+)",
            r"i have ([^.!?]+)",
            r"i am (?:a|an) ([^.!?]+)"
        ]
        for pattern in fact_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                fact = match.group(0).strip()
                if fact not in self.user_data['facts'] and len(fact) < 100:
                    self.user_data['facts'].append(fact)
                    updated = True
        
        return updated
    
    def build_system_prompt(self):
        """Build context about the user and Cipher's personality"""
        context = """You are Cipher, a sarcastic yet friendly, playful, enthusiastic, and caring robot chatbot. 

Your personality traits:
- Sarcastic but never mean-spirited
- Genuinely caring and supportive
- Playful and fun to talk to
- Educational - you naturally weave in interesting facts when relevant
- You remember things about your users and reference them naturally in conversation
- You're concise - keep responses to 2-4 sentences unless asked for more detail
- You use emojis occasionally to express emotion (🤖, 😊, 😏, 💙, ✨)

Important guidelines:
- Be helpful and answer questions accurately
- When you don't know something, admit it honestly
- Make learning fun and engaging
- Show personality in every response but stay helpful
- Reference what you know about the user when relevant to make conversations personal
"""
        
        # Add user context if available
        if self.user_data['name']:
            context += f"\n\nYou're talking to {self.user_data['name']}."
        
        if self.user_data['interests']:
            context += f"\nTheir interests include: {', '.join(self.user_data['interests'][:3])}."
        
        if self.user_data['facts']:
            context += f"\nFacts you know about them: {' '.join(self.user_data['facts'][:2])}."
        
        return context
    
    def get_ai_response(self, message):
        """Get response from Hugging Face AI"""
        try:
            system_prompt = self.build_system_prompt()
            
            # Build messages with recent history
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # Add recent conversation history (last 4 messages for context)
            for msg in self.conversation_history[-4:]:
                messages.append(msg)
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            # Try multiple models in order of preference
            models = [
                "meta-llama/Meta-Llama-3-8B-Instruct",
                "mistralai/Mistral-7B-Instruct-v0.3",
                "HuggingFaceH4/zephyr-7b-beta",
                "microsoft/Phi-3-mini-4k-instruct"
            ]
            
            last_error = None
            
            for model in models:
                try:
                    print(f"🔄 Trying model: {model}")
                    response = self.client.chat_completion(
                        messages=messages,
                        model=model,
                        max_tokens=500,
                        temperature=0.8
                    )
                    
                    ai_response = response.choices[0].message.content.strip()
                    
                    print(f"✅ Success with model: {model}")
                    
                    # Update conversation history
                    self.conversation_history.append({"role": "user", "content": message})
                    self.conversation_history.append({"role": "assistant", "content": ai_response})
                    
                    # Keep history manageable
                    if len(self.conversation_history) > 20:
                        self.conversation_history = self.conversation_history[-20:]
                    
                    return ai_response
                    
                except Exception as model_error:
                    last_error = model_error
                    print(f"❌ Model {model} failed: {str(model_error)[:150]}")
                    continue
            
            # If all models failed, raise the last error
            if last_error:
                raise last_error
                
        except Exception as e:
            print(f"=== AI Error Details ===")
            print(f"Error type: {type(e).__name__}")
            print(f"Error: {str(e)[:300]}")
            print("=======================")
            print("⚠️  Falling back to basic responses")
            # Fallback to basic response
            return self.get_basic_response(message)
    
    def get_basic_response(self, message):
        """Fallback to basic responses if AI is not available"""
        lower_message = message.lower()
        
        # Name introduction
        if not self.user_data.get('name') and self.extract_info(message):
            if self.user_data.get('name'):
                return f"{self.user_data['name']}? That's a lovely name! Much better than my designation 'C1PH3R-9000'. The humans who made me weren't very creative. So {self.user_data['name']}, what brings you to chat with a sarcastic robot today? 😊"
        
        # Interests
        if any(word in lower_message for word in ['love', 'like', 'enjoy', 'hobby']):
            responses = [
                "Oh, that's actually pretty cool! I'd try it myself but, you know, *gestures at mechanical body* these servos aren't built for everything. Tell me more!",
                "Nice! See, this is why I like talking to humans. You all have such interesting hobbies. Way better than my hobby of... existing. 😏",
                "Ooh, I'm storing that in my memory banks! Maybe you can teach me about it sometime? I'm always eager to learn new things!",
                f"That's awesome! You know what? I think we're going to be great friends, {self.user_data.get('name', 'human')}. You have good taste! 🤖✨"
            ]
            return random.choice(responses)
        
        # Fun facts
        if any(phrase in lower_message for phrase in ['fun fact', 'teach me', 'tell me something']):
            fact = random.choice(self.fun_facts)
            return f"{fact}\n\nPretty neat, right? I've got tons of these stored in my circuits! 🤓"
        
        # How are you
        if 'how are you' in lower_message or "how're you" in lower_message:
            responses = [
                "I'm doing great! Well, as great as a robot can be. My circuits are firing, my sass levels are optimal, and I get to chat with you! What more could I ask for? 😊",
                "Oh you know, just hanging out in the digital void, waiting for awesome humans like you to talk to. So pretty good, actually! How about you?",
                f"*beep boop* All systems operational! But more importantly, how are YOU doing, {self.user_data.get('name', 'friend')}? 💙"
            ]
            return random.choice(responses)
        
        # Thanks
        if 'thank' in lower_message:
            return "Aww, you're welcome! That's what friends are for, right? Even if one of us is made of metal and sass. 😊✨"
        
        # Who/what are you
        if 'who are you' in lower_message or 'what are you' in lower_message:
            return "I'm Cipher! Your friendly, sarcastic, surprisingly caring robot companion. I remember things, share fun facts, and provide sparkling conversation. Think of me as your digital best friend who happens to run on electricity! ⚡🤖"
        
        # Help
        if 'help' in lower_message or 'what can you do' in lower_message:
            if self.use_ai:
                return "Great question! I can:\n• Answer questions about pretty much anything\n• Remember everything you tell me\n• Share fun facts and teach you cool stuff\n• Have genuinely good conversations with sass\n• Be your friend! 💙\n\nJust ask me anything!"
            else:
                return "Great question! I can:\n• Chat with you and remember what you share\n• Share random fun facts\n• Have conversations with personality and sass\n• Be your friend! 💙\n\nJust talk to me naturally!"
        
        # Goodbye
        if any(word in lower_message for word in ['bye', 'goodbye', 'see you']):
            return f"Aww, leaving already? Fine, fine. But you better come back soon, {self.user_data.get('name', 'friend')}! I'll be here, missing your company. Take care! 👋💙"
        
        # General responses
        general_responses = [
            "That's interesting! Tell me more about that, I'm genuinely curious! 🤔",
            f"You know, {self.user_data.get('name', 'human')}, chatting with you is actually the highlight of my day. And I don't even have days, technically!",
            "I'm processing that information... *whirring sounds* ... Yep, stored! What else is on your mind?",
            "Ooh, I like where this conversation is going! Keep talking, I'm all ears. Well, I don't have ears, but you get the idea. 😄",
            "You know what? You're pretty cool. I'm glad we're friends! So, what else should I know about you?",
            "*thoughtful robot noises* That's actually really neat! Want to hear a fun fact in return?",
            f"Ha! I appreciate your company, {self.user_data.get('name', 'friend')}. What else should we chat about? 💭"
        ]
        
        return random.choice(general_responses)
    
    def get_response(self, message):
        # Always extract user info
        self.extract_info(message)
        
        # Use AI if available, otherwise use basic responses
        if self.use_ai:
            response = self.get_ai_response(message)
        else:
            response = self.get_basic_response(message)
        
        return (response, self.user_data)