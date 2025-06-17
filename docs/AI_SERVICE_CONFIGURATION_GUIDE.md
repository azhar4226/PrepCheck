# AI Service Configuration Guide

## ✅ Real AI is Now the Default!

The PrepCheck AI service now defaults to using **real Gemini AI** for quiz generation, providing high-quality, varied questions with educational explanations.

## 🔄 AI Service Modes

### **Real AI Mode (Default)**
- **Description**: Uses Google's Gemini AI for intelligent quiz generation
- **Quality**: High-quality, contextually accurate questions
- **Speed**: 2-8 seconds per quiz (depends on AI API response time)
- **Usage**: Recommended for production and quality testing

### **Mock AI Mode**
- **Description**: Uses optimized mock service for ultra-fast generation
- **Quality**: Good quality with pre-defined patterns
- **Speed**: < 0.1 seconds per quiz (lightning fast)
- **Usage**: Recommended for development and rapid testing

## 🚀 How to Control AI Mode

### **Default Configuration (Real AI)**
```bash
# No environment variable needed - real AI is default
python app.py
```

### **Force Mock AI for Development**
```bash
# Set environment variable to force mock mode
FORCE_AI_MOCK=true python app.py
```

### **Explicitly Use Real AI**
```bash
# Explicitly set to false (though this is the default)
FORCE_AI_MOCK=false python app.py
```

## ⚙️ Environment Configuration

### **In .env file:**
```properties
# Gemini AI Configuration
GEMINI_API_KEY=your_api_key_here

# AI Service Mode (default: real AI)
# Uncomment the line below to force mock mode for development
# FORCE_AI_MOCK=true
```

### **Environment Variables:**
- `GEMINI_API_KEY`: Your Google Gemini API key (required for real AI)
- `FORCE_AI_MOCK`: Set to `true` to force mock mode, `false` or unset for real AI

## 📊 Performance Comparison

| Mode | Generation Time | Quality | Best For |
|------|----------------|---------|----------|
| Real AI (Default) | 2-8 seconds | Excellent | Production, Quality Testing |
| Mock AI | < 0.1 seconds | Good | Development, Rapid Testing |

## 🔍 How to Verify Which Mode is Active

### **Check Server Logs:**
```bash
# Real AI Mode:
✅ Gemini AI service initialized successfully - using real AI
🤖 Using real AI quiz generation

# Mock AI Mode:
🎭 Forcing mock AI service for development
🎭 Using mock quiz generation
```

### **Check API Response:**
```json
{
  "ai_metadata": {
    "model_used": "Gemini-1.5-Flash",  // Real AI
    // OR
    "model_used": "Mock",              // Mock AI
    "generation_time": 3.56           // Time taken
  }
}
```

## 🛠️ Advanced Features

### **Automatic Fallback**
Real AI mode includes intelligent fallback to mock service if:
- AI API is unavailable
- JSON parsing fails
- Request times out
- API key is invalid

### **Improved JSON Parsing**
Real AI mode includes advanced JSON cleanup to handle:
- Malformed JSON responses
- Trailing commas
- Unescaped quotes
- Missing property quotes

### **Performance Monitoring**
Both modes include detailed performance logging:
- Generation time tracking
- Database operation timing
- Error reporting and fallback logging

## 🎯 Recommendations

### **For Development:**
```bash
# Use mock AI for rapid iteration
FORCE_AI_MOCK=true python app.py
```

### **For Testing:**
```bash
# Use real AI to test quality and integration
python app.py  # (real AI is default)
```

### **For Production:**
```bash
# Use real AI with proper API key
GEMINI_API_KEY=your_production_key python app.py
```

## 🚨 Troubleshooting

### **Real AI Not Working:**
1. Check `GEMINI_API_KEY` is set correctly
2. Verify API key has proper permissions
3. Check internet connectivity
4. Review server logs for error messages

### **Slow Performance:**
1. Use mock mode for development: `FORCE_AI_MOCK=true`
2. Reduce number of questions for testing
3. Check AI API rate limits

### **JSON Parsing Errors:**
- The system will automatically fallback to mock generation
- Check server logs for detailed error information
- Report persistent issues for further optimization

## ✅ Status: Configured

Real AI is now the default mode, providing high-quality quiz generation while maintaining the option for ultra-fast mock generation during development.

**The system intelligently balances quality and performance based on your needs!**
