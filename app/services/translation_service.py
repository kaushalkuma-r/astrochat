import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from IndicTransToolkit.processor import IndicProcessor
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class TranslationService:
    """Service for translating horoscope responses to different languages using IndicTrans2."""
    
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self.tokenizer = None
        self.processor = None
        self.is_initialized = False
        
        # Supported language mappings
        self.supported_languages = {
            "en": "eng_Latn",
            "hi": "hin_Deva", 
            "bn": "ben_Beng",
            "ta": "tam_Taml",
            "te": "tel_Telu",
            "mr": "mar_Deva",
            "gu": "guj_Gujr",
            "kn": "kan_Knda",
            "ml": "mal_Mlym",
            "pa": "pan_Guru",
            "or": "ory_Orya",
            "as": "asm_Beng"
        }
        
        # Initialize the model
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the IndicTrans2 model and tokenizer."""
        try:
            logger.info("🚀 Initializing IndicTrans2 translation model...")
            
            model_name = "ai4bharat/indictrans2-en-indic-1B"
            logger.info(f"📥 Model name: {model_name}")
            
            # Check if model is already downloaded
            from transformers import AutoConfig
            try:
                logger.info("🔍 Checking if model is already downloaded...")
                config = AutoConfig.from_pretrained(model_name, trust_remote_code=True)
                logger.info(f"✅ Model config loaded successfully")
                logger.info(f"📊 Model config: {config}")
                
                # Check cache directory
                from transformers import TRANSFORMERS_CACHE
                import os
                logger.info(f"📁 Transformers cache directory: {TRANSFORMERS_CACHE}")
                if os.path.exists(TRANSFORMERS_CACHE):
                    logger.info(f"📁 Cache directory exists")
                    cache_contents = os.listdir(TRANSFORMERS_CACHE)
                    logger.info(f"📁 Cache contents: {cache_contents}")
                else:
                    logger.info(f"📁 Cache directory does not exist")
                    
            except Exception as e:
                logger.error(f"❌ Failed to load model config: {e}")
                raise
            
            # Load tokenizer
            logger.info("🔧 Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name, 
                trust_remote_code=True
            )
            logger.info(f"✅ Tokenizer loaded successfully")
            logger.info(f"📊 Tokenizer vocab size: {self.tokenizer.vocab_size}")
            
            # Load model
            logger.info("🔧 Loading model...")
            self.model = AutoModelForSeq2SeqLM.from_pretrained(
                model_name,
                trust_remote_code=True,
                torch_dtype=torch.float16,
                attn_implementation="flash_attention_2" if torch.cuda.is_available() else "eager"
            ).to(self.device)
            logger.info(f"✅ Model loaded successfully")
            logger.info(f"📊 Model parameters: {sum(p.numel() for p in self.model.parameters()):,}")
            
            # Initialize processor
            logger.info("🔧 Initializing processor...")
            self.processor = IndicProcessor(inference=True)
            logger.info(f"✅ Processor initialized successfully")
            
            # Test the model with a simple translation
            logger.info("🧪 Testing model with simple translation...")
            test_result = self._test_translation("Hello", "hi")
            logger.info(f"🧪 Test translation result: {test_result}")
            
            self.is_initialized = True
            logger.info(f"✅ Translation model initialized successfully on {self.device}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize translation model: {e}")
            import traceback
            logger.error(f"❌ Full traceback: {traceback.format_exc()}")
            self.is_initialized = False
    
    def _test_translation(self, text: str, target_lang: str) -> str:
        """Test translation with a simple example."""
        try:
            # Get target language code
            tgt_lang = self.supported_languages.get(target_lang.lower())
            if not tgt_lang:
                return f"Unsupported language: {target_lang}"
            
            # Source language is English
            src_lang = "eng_Latn"
            
            logger.info(f"🧪 Test: Translating '{text}' from {src_lang} to {tgt_lang}")
            
            # Preprocess the text
            batch = self.processor.preprocess_batch(
                [text],
                src_lang=src_lang,
                tgt_lang=tgt_lang,
            )
            logger.info(f"🧪 Test: Preprocessed batch: {batch}")
            
            # Tokenize
            inputs = self.tokenizer(
                batch,
                truncation=True,
                padding="longest",
                return_tensors="pt",
                return_attention_mask=True,
            ).to(self.device)
            logger.info(f"🧪 Test: Tokenized inputs shape: {inputs['input_ids'].shape}")
            
            # Generate translation
            with torch.no_grad():
                generated_tokens = self.model.generate(
                    **inputs,
                    use_cache=True,
                    min_length=0,
                    max_length=256,
                    num_beams=5,
                    num_return_sequences=1,
                )
            logger.info(f"🧪 Test: Generated tokens shape: {generated_tokens.shape}")
            
            # Decode tokens
            generated_tokens = self.tokenizer.batch_decode(
                generated_tokens,
                skip_special_tokens=True,
                clean_up_tokenization_spaces=True,
            )
            logger.info(f"🧪 Test: Decoded tokens: {generated_tokens}")
            
            # Postprocess
            translations = self.processor.postprocess_batch(generated_tokens, lang=tgt_lang)
            logger.info(f"🧪 Test: Postprocessed translations: {translations}")
            
            if translations and len(translations) > 0:
                result = translations[0]
                logger.info(f"🧪 Test: Final result: {result}")
                return result
            else:
                logger.warning("🧪 Test: Translation returned empty result")
                return "Translation failed"
                
        except Exception as e:
            logger.error(f"❌ Test translation error: {e}")
            import traceback
            logger.error(f"❌ Test translation traceback: {traceback.format_exc()}")
            return f"Test translation error: {e}"
    
    def translate_text(self, text: str, target_language: str) -> Optional[str]:
        """
        Translate text to the target language.
        
        Args:
            text: Text to translate
            target_language: Target language code (e.g., 'hi', 'bn', 'ta')
            
        Returns:
            Translated text or None if translation fails
        """
        if not self.is_initialized:
            logger.warning("Translation model not initialized")
            return None
        
        if not text or not text.strip():
            return text
        
        try:
            # Get target language code
            tgt_lang = self.supported_languages.get(target_language.lower())
            if not tgt_lang:
                logger.warning(f"Unsupported target language: {target_language}")
                return None
            
            # Source language is English
            src_lang = "eng_Latn"
            
            logger.info(f"🌐 Translating text to {target_language} ({tgt_lang})")
            logger.info(f"📝 Input text: {text}")
            logger.info(f"🔤 Source lang: {src_lang}, Target lang: {tgt_lang}")
            
            # Preprocess the text
            logger.info("🔧 Preprocessing text...")
            batch = self.processor.preprocess_batch(
                [text],
                src_lang=src_lang,
                tgt_lang=tgt_lang,
            )
            logger.info(f"📦 Preprocessed batch: {batch}")
            
            # Tokenize
            inputs = self.tokenizer(
                batch,
                truncation=True,
                padding="longest",
                return_tensors="pt",
                return_attention_mask=True,
            ).to(self.device)
            
            # Generate translation
            with torch.no_grad():
                generated_tokens = self.model.generate(
                    **inputs,
                    use_cache=True,
                    min_length=0,
                    max_length=256,
                    num_beams=5,
                    num_return_sequences=1,
                )
            
            # Decode tokens
            generated_tokens = self.tokenizer.batch_decode(
                generated_tokens,
                skip_special_tokens=True,
                clean_up_tokenization_spaces=True,
            )
            
            # Postprocess
            translations = self.processor.postprocess_batch(generated_tokens, lang=tgt_lang)
            
            logger.info(f"🔍 DEBUG: Generated tokens: {generated_tokens}")
            logger.info(f"🔍 DEBUG: Postprocessed translations: {translations}")
            
            if translations and len(translations) > 0:
                translated_text = translations[0]
                logger.info(f"✅ Translation successful: {len(text)} chars -> {len(translated_text)} chars")
                logger.info(f"📝 Original: {text}")
                logger.info(f"📝 Translated: {translated_text}")
                return translated_text
            else:
                logger.warning("Translation returned empty result")
                return None
                
        except Exception as e:
            logger.error(f"❌ Translation error: {e}")
            # Try with simpler generation parameters
            try:
                logger.info("🔄 Retrying with simpler generation parameters...")
                with torch.no_grad():
                    generated_tokens = self.model.generate(
                        **inputs,
                        use_cache=False,
                        min_length=0,
                        max_length=128,
                        num_beams=1,
                        num_return_sequences=1,
                        do_sample=False,
                    )
                
                # Decode tokens
                generated_tokens = self.tokenizer.batch_decode(
                    generated_tokens,
                    skip_special_tokens=True,
                    clean_up_tokenization_spaces=True,
                )
                
                # Postprocess
                translations = self.processor.postprocess_batch(generated_tokens, lang=tgt_lang)
                
                if translations and len(translations) > 0:
                    translated_text = translations[0]
                    logger.info(f"✅ Translation successful (retry): {len(text)} chars -> {len(translated_text)} chars")
                    return translated_text
                else:
                    logger.warning("Translation retry returned empty result")
                    return None
                    
            except Exception as e2:
                logger.error(f"❌ Translation retry also failed: {e2}")
                return None
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get list of supported languages."""
        return self.supported_languages.copy()
    
    def is_language_supported(self, language_code: str) -> bool:
        """Check if a language is supported."""
        return language_code.lower() in self.supported_languages
    
    def translate_horoscope_response(self, response: Dict[str, Any], target_language: str) -> Optional[Dict[str, Any]]:
        """
        Translate a horoscope response to the target language.
        
        Args:
            response: Horoscope response dictionary
            target_language: Target language code
            
        Returns:
            Translated response or None if translation fails
        """
        if not self.is_language_supported(target_language):
            logger.warning(f"Unsupported language: {target_language}")
            return None
        
        try:
            # Translate the insight
            original_insight = response.get("insight", "")
            if not original_insight:
                logger.warning("No insight to translate")
                return None
            
            translated_insight = self.translate_text(original_insight, target_language)
            if not translated_insight:
                logger.warning("Translation failed")
                return None
            
            # Create translated response
            translated_response = response.copy()
            translated_response["insight"] = translated_insight
            translated_response["language"] = target_language
            
            logger.info(f"✅ Horoscope translated to {target_language}")
            return translated_response
            
        except Exception as e:
            logger.error(f"❌ Error translating horoscope response: {e}")
            return None
