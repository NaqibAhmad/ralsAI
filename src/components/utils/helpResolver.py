import asyncio
import logging
from typing import List, Tuple, Set
import discord
from src.components.agents.GroqAgent import agent
from src.components.utils.intentClassifier import is_helpful_category, is_helpful_channel

# Set up comprehensive logging with UTF-8 encoding
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('discord_bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# Configure the console handler to use UTF-8 encoding
console_handler = None
for handler in logging.getLogger().handlers:
    if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler):
        console_handler = handler
        break

if console_handler:
    # Set UTF-8 encoding for console output
    import sys
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')
        
# Suppress verbose httpx logs
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger('HelpResolver')

class OptimizedHelpResolver:
    def __init__(self, batch_size: int = 3, max_messages_per_channel: int =100):
        self.batch_size = batch_size
        self.max_messages_per_channel = max_messages_per_channel
        self.category_cache = {}  # Cache category classifications
        self.channel_cache = {}   # Cache channel classifications
        self.stats = {
            'total_searches': 0,
            'cache_hits': 0,
            'api_calls': 0,
            'avg_response_time': 0
        }
        
    async def batch_classify_categories(self, categories: List[discord.CategoryChannel], user_message: str) -> List[discord.CategoryChannel]:
        """Classify multiple categories in parallel batches"""
        logger.info(f"🏷️ Starting category classification for {len(categories)} categories")
        helpful_categories = []
        cache_hits = 0
        api_calls = 0
        
        # Process categories in batches to avoid rate limits
        for i in range(0, len(categories), self.batch_size):
            batch = categories[i:i + self.batch_size]
            logger.debug(f"📦 Processing category batch {i//self.batch_size + 1}: {[c.name for c in batch]}")
            
            # Create classification tasks for this batch
            tasks = []
            for category in batch:
                cache_key = f"{category.name}:{user_message}"
                if cache_key in self.category_cache:
                    cache_hits += 1
                    if self.category_cache[cache_key]:
                        helpful_categories.append(category)
                        logger.debug(f"💾 Cache hit for category: {category.name} (helpful)")
                    else:
                        logger.debug(f"💾 Cache hit for category: {category.name} (not helpful)")
                    continue
                
                tasks.append(self._classify_category_with_cache(category, user_message, cache_key))
                api_calls += 1
            
            # Wait for batch to complete
            if tasks:
                logger.debug(f"🔄 Executing {len(tasks)} classification tasks")
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for j, result in enumerate(batch_results):
                    if isinstance(result, Exception):
                        logger.error(f"❌ Error classifying category {batch[j].name}: {result}")
                        continue
                    
                    category, is_helpful = result
                    if is_helpful:
                        helpful_categories.append(category)
                        logger.info(f"✅ Category '{category.name}' marked as helpful")
                    else:
                        logger.debug(f"⚪ Category '{category.name}' marked as not helpful")
        
        logger.info(f"🎯 Category classification complete: {len(helpful_categories)}/{len(categories)} helpful (Cache hits: {cache_hits}, API calls: {api_calls})")
        self.stats['cache_hits'] += cache_hits
        self.stats['api_calls'] += api_calls
        return helpful_categories

    async def _classify_category_with_cache(self, category: discord.CategoryChannel, user_message: str, cache_key: str) -> Tuple[discord.CategoryChannel, bool]:
        """Classify a single category and cache the result"""
        try:
            logger.debug(f"🔍 Classifying category: {category.name}")
            is_helpful = await is_helpful_category(category.name, user_message)
            self.category_cache[cache_key] = is_helpful
            logger.debug(f"💾 Cached result for category {category.name}: {is_helpful}")
            return category, is_helpful
        except Exception as e:
            logger.error(f"❌ Error classifying category {category.name}: {e}")
            return category, False

    async def batch_classify_channels(self, channels: List[discord.TextChannel], user_message: str) -> List[discord.TextChannel]:
        """Classify multiple channels in parallel batches"""
        logger.info(f"📺 Starting channel classification for {len(channels)} channels")
        helpful_channels = []
        cache_hits = 0
        api_calls = 0
        
        # Process channels in batches
        for i in range(0, len(channels), self.batch_size):
            batch = channels[i:i + self.batch_size]
            logger.debug(f"📦 Processing channel batch {i//self.batch_size + 1}: {[c.name for c in batch]}")
            
            tasks = []
            for channel in batch:
                cache_key = f"{channel.name}:{channel.topic or ''}:{user_message}"
                if cache_key in self.channel_cache:
                    cache_hits += 1
                    if self.channel_cache[cache_key]:
                        helpful_channels.append(channel)
                        logger.debug(f"💾 Cache hit for channel: #{channel.name} (helpful)")
                    else:
                        logger.debug(f"💾 Cache hit for channel: #{channel.name} (not helpful)")
                    continue
                
                tasks.append(self._classify_channel_with_cache(channel, user_message, cache_key))
                api_calls += 1
            
            if tasks:
                logger.debug(f"🔄 Executing {len(tasks)} channel classification tasks")
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for j, result in enumerate(batch_results):
                    if isinstance(result, Exception):
                        logger.error(f"❌ Error classifying channel {batch[j].name}: {result}")
                        continue
                    
                    channel, is_helpful = result
                    if is_helpful:
                        helpful_channels.append(channel)
                        logger.info(f"✅ Channel '#{channel.name}' marked as helpful")
                    else:
                        logger.debug(f"⚪ Channel '#{channel.name}' marked as not helpful")
        
        logger.info(f"🎯 Channel classification complete: {len(helpful_channels)}/{len(channels)} helpful (Cache hits: {cache_hits}, API calls: {api_calls})")
        self.stats['cache_hits'] += cache_hits
        self.stats['api_calls'] += api_calls
        return helpful_channels

    async def _classify_channel_with_cache(self, channel: discord.TextChannel, user_message: str, cache_key: str) -> Tuple[discord.TextChannel, bool]:
        """Classify a single channel and cache the result"""
        try:
            logger.debug(f"🔍 Classifying channel: #{channel.name}")
            topic = channel.topic or ""
            is_helpful = await is_helpful_channel(channel.name, user_message, topic)
            self.channel_cache[cache_key] = is_helpful
            logger.debug(f"💾 Cached result for channel #{channel.name}: {is_helpful}")
            return channel, is_helpful
        except Exception as e:
            logger.error(f"❌ Error classifying channel #{channel.name}: {e}")
            return channel, False

    async def parallel_message_collection(self, channels: List[discord.TextChannel], guild: discord.Guild) -> List[Tuple[str, str, str]]:
        """Collect messages from multiple channels in parallel"""
        logger.info(f"📨 Starting message collection from {len(channels)} channels")
        
        tasks = []
        for channel in channels:
            tasks.append(self._collect_channel_messages(channel, guild))
        
        # Collect all messages in parallel
        logger.debug(f"🔄 Executing {len(tasks)} message collection tasks")
        channel_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_messages = []
        successful_channels = 0
        for i, result in enumerate(channel_results):
            if isinstance(result, Exception):
                logger.error(f"❌ Error collecting messages from #{channels[i].name}: {result}")
                continue
            
            successful_channels += 1
            channel_message_count = len(result)
            logger.debug(f"📊 Collected {channel_message_count} messages from #{channels[i].name}")
            all_messages.extend(result)
        
        logger.info(f"📊 Message collection complete: {len(all_messages)} total messages from {successful_channels}/{len(channels)} channels")
        return all_messages

    async def _collect_channel_messages(self, channel: discord.TextChannel, guild: discord.Guild) -> List[Tuple[str, str, str]]:
        """Collect messages from a single channel"""
        messages = []
        try:
            logger.debug(f"📖 Reading messages from #{channel.name} (limit: {self.max_messages_per_channel})")
            message_count = 0
            
            async for message in channel.history(limit=self.max_messages_per_channel):
                # Skip bot's own messages
                if message.author.id == guild.me.id:
                    continue
                
                # Get text content
                text_content = message.content.strip()
                
                # Extract embed content
                embed_content = ""
                for embed in message.embeds:
                    title = embed.title or ""
                    desc = embed.description or ""
                    fields = "\n".join(f"{f.name}: {f.value}" for f in embed.fields)
                    embed_content += f"{title}\n{desc}\n{fields}\n"
                
                full_content = (text_content + "\n" + embed_content).strip()
                
                if full_content:
                    messages.append((channel.name, message.author.display_name, full_content))
                    message_count += 1
            
            logger.debug(f"✅ Successfully collected {message_count} messages from #{channel.name}")
            logger.debug(f"📖 Finished reading messages from #{channel.name}")
            logger.info(f"📖 Collected {len(messages)} messages from #{channel.name}")
            logger.info(f"📖 Messages: {messages}")
                    
        except Exception as e:
            logger.error(f"❌ Error collecting messages from #{channel.name}: {e}")
        
        return messages

    async def smart_search_with_keywords(self, guild: discord.Guild, user_message: str) -> List[Tuple[str, str, str]]:
        """Use keyword-based pre-filtering before AI classification"""
        logger.info(f"🚀 Starting smart search in server '{guild.name}' for query: '{user_message}'")
        
        # Extract potential keywords from user message
        keywords = self._extract_keywords(user_message.lower())
        logger.info(f"🔍 Extracted keywords: {list(keywords)}")
        
        # Pre-filter channels based on keywords
        candidate_channels = []
        keyword_matched_channels = 0
        
        for category in guild.categories:
            # Check category name against keywords
            if any(keyword in category.name.lower() for keyword in keywords):
                candidate_channels.extend(category.text_channels)
                keyword_matched_channels += len(category.text_channels)
                logger.debug(f"🎯 Category '{category.name}' matched keywords - added {len(category.text_channels)} channels")
                continue
                
            # Check channel names and topics
            for channel in category.text_channels:
                channel_text = f"{channel.name} {channel.topic or ''}".lower()
                if any(keyword in channel_text for keyword in keywords):
                    candidate_channels.append(channel)
                    keyword_matched_channels += 1
                    logger.debug(f"🎯 Channel '#{channel.name}' matched keywords")
        
        # Also include channels with generic help-related names
        help_keywords = ['help', 'support', 'question', 'ask', 'general', 'chat', 'discussion', 'info', 'faq', 'announcements', 'tournament', 'event']
        help_matched_channels = 0
        for category in guild.categories:
            for channel in category.text_channels:
                channel_name = channel.name.lower()
                if any(help_keyword in channel_name for help_keyword in help_keywords):
                    if channel not in candidate_channels:
                        candidate_channels.append(channel)
                        help_matched_channels += 1
                        logger.debug(f"🆘 Channel '#{channel.name}' matched help keywords")
        
        logger.info(f"🎯 Pre-filtering complete: {len(candidate_channels)} candidate channels (Keyword: {keyword_matched_channels}, Help: {help_matched_channels})")
        
        # Now use AI classification only on candidate channels
        if candidate_channels:
            helpful_channels = await self.batch_classify_channels(candidate_channels, user_message)
            logger.info(f"✅ AI classified {len(helpful_channels)} channels as helpful")
            
            # Collect messages in parallel
            return await self.parallel_message_collection(helpful_channels, guild)
        
        logger.warning("⚠️ No candidate channels found")
        return []

    def _extract_keywords(self, message: str) -> Set[str]:
        """Extract relevant keywords from user message"""
        # Remove common words
        stop_words = {'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'but', 'in', 'with', 'to', 'for', 'of', 'as', 'by', 'how', 'what', 'where', 'when', 'why', 'i', 'me', 'my', 'we', 'our', 'you', 'your'}
        
        words = message.replace('?', '').replace('!', '').replace('.', '').split()
        keywords = {word for word in words if len(word) > 2 and word not in stop_words}
        
        logger.debug(f"🔤 Keyword extraction: '{message}' → {keywords}")
        return keywords

    def log_performance_stats(self):
        """Log current performance statistics"""
        logger.info(f"📊 Performance Stats - Total searches: {self.stats['total_searches']}, "
                   f"Cache hits: {self.stats['cache_hits']}, API calls: {self.stats['api_calls']}, "
                   f"Avg response time: {self.stats['avg_response_time']:.2f}s")

# Updated main function
async def search_messages_for_help_optimized(guild: discord.Guild, message: discord.Message, limit_per_channel=100):
    """Optimized version of the help search function"""
    resolver = OptimizedHelpResolver(batch_size=3, max_messages_per_channel=limit_per_channel)
    
    logger.info(f"🚀 Starting optimized help search for user {message.author.display_name} in server '{guild.name}'")
    logger.info(f"📝 User query: '{message.content}'")
    start_time = asyncio.get_event_loop().time()
    
    # Update stats
    resolver.stats['total_searches'] += 1
    
    # Use smart keyword-based search with AI classification
    collected_messages = await resolver.smart_search_with_keywords(guild, message.content)
    
    end_time = asyncio.get_event_loop().time()
    response_time = end_time - start_time
    
    # Update average response time
    resolver.stats['avg_response_time'] = (
        (resolver.stats['avg_response_time'] * (resolver.stats['total_searches'] - 1) + response_time) / 
        resolver.stats['total_searches']
    )
    
    logger.info(f"⏱️ Search completed in {response_time:.2f} seconds")
    logger.info(f"📊 Final results: {len(collected_messages)} messages collected")
    resolver.log_performance_stats()
    
    return collected_messages

# Updated handle_help_request function with user feedback
async def handle_help_request_optimized(message: discord.Message):
    """Optimized version of handle_help_request with user feedback"""
    guild = message.guild
    user_mention = message.author.mention
    
    logger.info(f"🆘 Help request from {message.author.display_name} ({message.author.id}): '{message.content}'")
    
    # Send initial acknowledgment message
    thinking_message = await message.channel.send(f"{user_mention} 🔍 Searching through the server for helpful information... This might take a moment!")
    
    try:
        # Search for help messages
        logger.info("🔄 Starting help message search...")
        help_messages = await search_messages_for_help_optimized(guild, message)

        if not help_messages:
            logger.warning("⚠️ No helpful messages found")
            await thinking_message.edit(content=f"{user_mention} I couldn't find any relevant help information in the server.")
            return

        # Limit to most relevant messages
        limited_messages = help_messages[:100]
        logger.info(f"📋 Using {len(limited_messages)} most relevant messages for response generation")
        
        combined = "\n".join(
            f"[#{ch}] {author}: {content}" for ch, author, content in limited_messages
        )

        # Update user that we're generating response
        await thinking_message.edit(content=f"{user_mention} ✨ Found relevant information! Generating your personalized response...")
        
        logger.info("🤖 Generating AI response...")
        help_summary_prompt = f"""
        The user said: '{message.content}'.
        Here are some recent messages that might be helpful:

        {combined}

        Based on the above, provide a useful, helpful response. If you can answer their question directly, do so. 
        If not, summarize what kinds of help or information is available.
        """

        response = await agent.arun(message=help_summary_prompt)
        final_response = getattr(response, 'content', "🤖 I tried, but couldn't generate a helpful answer.")
        
        # Send final response
        await thinking_message.edit(content=f"{user_mention} {final_response}")
        logger.info("✅ Help request successfully handled")
        
    except Exception as e:
        logger.error(f"❌ Error handling help request: {e}")
        await thinking_message.edit(content=f"{user_mention} Sorry, I encountered an error while searching for help. Please try again later.")
        
    logger.info("🏁 Help request processing complete")