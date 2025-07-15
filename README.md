# NBP Sales Preparation Tool

A comprehensive Streamlit application for NBP (National Business Partners) sales representatives to manage prospects, extract data from websites and LinkedIn, generate AI-powered sales scripts, and improve their sales pitch effectiveness.

## 🚀 Features

### Core Functionality
- **User Authentication**: Secure login with hardcoded credentials (username: "sales_rep", password: "nbp2025")
- **Prospect Management**: Complete CRUD operations for prospects and contacts
- **Database Integration**: SQLite database with comprehensive data models
- **Component-Based Architecture**: Modular, reusable UI components

### Data Extraction Features
- **Website Data Extraction**: 
  - URL validation and parsing
  - Company information extraction (name, description, industry)
  - Contact information extraction (emails, phone numbers)
  - Social media link detection
  - Industry and company size detection
  - Error handling for invalid URLs and connection issues

- **LinkedIn Profile Extraction**:
  - LinkedIn URL validation and parsing
  - Profile type detection (individual vs company)
  - Username and company name extraction
  - Structured data extraction capabilities

- **Bulk Extraction**:
  - Process multiple URLs simultaneously
  - Progress tracking and status updates
  - Comprehensive error handling

### AI Script Generation
- **OpenAI Integration**: GPT-4 and GPT-3.5-turbo support
- **Script Types**: 8 different script types including:
  - Cold Call Scripts
  - Email Templates
  - Meeting Agendas
  - Follow-up Messages
  - Presentation Outlines
  - Objection Handling
  - Closing Scripts
  - Social Media Posts

- **Customization Options**:
  - 6 different tones (Professional, Friendly, Consultative, etc.)
  - 10 focus areas (Value Proposition, Pain Points, Benefits & ROI, etc.)
  - Adjustable creativity and token limits
  - Custom context input

- **Script Management**:
  - Save generated scripts to database
  - View script history
  - Copy and download functionality
  - Integration with prospect data

### Prospect Management
- **Comprehensive Forms**: Detailed prospect information capture
- **Contact Management**: Multiple contacts per prospect
- **NBP Business Categories**: 24 predefined business categories
- **Meeting Objectives**: 6 different meeting types
- **Auto-fill Integration**: Use extracted data to populate forms

### Analytics & Reporting
- **User Statistics**: Track prospects, contacts, and scripts
- **Database Analytics**: Comprehensive system statistics
- **Performance Metrics**: Monitor user activity and engagement

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- OpenAI API key (for AI features)

### Setup
1. Clone the repository:
```bash
git clone <repository-url>
cd nbp-sales-tool
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables (optional):
```bash
# Create .env file
OPENAI_API_KEY=your_openai_api_key_here
```

4. Run the application:
```bash
streamlit run app.py
```

## 📋 Usage

### Authentication
- Username: `sales_rep`
- Password: `nbp2025`

### Data Extraction Workflow
1. Navigate to "Data Extraction" in the sidebar
2. Choose Website, LinkedIn, or Bulk extraction
3. Enter URLs and click "Extract Data"
4. Review extracted information
5. Click "Use Extracted Data in Form" to auto-fill prospect forms

### AI Script Generation Workflow
1. Navigate to "AI Script Generation"
2. Configure your OpenAI API key
3. Select a prospect or enter prospect information
4. Choose script type, tone, and focus areas
5. Add custom context if needed
6. Click "Generate Script"
7. Review, copy, or save the generated script

### Prospect Management Workflow
1. Navigate to "New Prospect" or "Quick Prospect"
2. Fill in company and contact information
3. Add additional contacts if needed
4. Submit the form to save the prospect
5. Use "My Pitches" to view and manage all prospects

## 🗄️ Database Schema

### Core Tables
- **users**: User authentication and profiles
- **prospects**: Company and prospect information
- **additional_contacts**: Multiple contacts per prospect
- **generated_scripts**: AI-generated sales scripts
- **sales_pitches**: User-created sales pitches
- **feedback**: Pitch feedback and ratings
- **analytics**: User activity tracking

### Key Features
- Foreign key relationships for data integrity
- Timestamp tracking for all records
- Comprehensive indexing for performance
- Soft delete capabilities

## 🔧 Configuration

### OpenAI API Setup
1. Get an API key from [OpenAI](https://platform.openai.com/)
2. Add it to the AI Script Generation settings
3. Test the connection with a simple script generation

### Extraction Settings
- Request timeout configuration
- Maximum email/phone extraction limits
- Social media link extraction toggles
- Bulk processing settings

## 📊 Analytics & Reporting

### User Dashboard
- Total prospects and contacts
- Recent activity tracking
- Script generation statistics
- Performance metrics

### System Analytics
- Database usage statistics
- User engagement metrics
- Feature utilization tracking
- Error rate monitoring

## 🚨 Error Handling

### Data Extraction
- Invalid URL validation
- Connection timeout handling
- Rate limiting protection
- Graceful degradation for failed extractions

### AI Generation
- API key validation
- Rate limit handling
- Model availability checks
- Content filtering and safety

### Database Operations
- Connection error handling
- Transaction rollback on failures
- Data validation before saving
- Comprehensive error logging

## 🔒 Security Features

- Hardcoded authentication (for demo purposes)
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- Secure API key handling

## 📈 Performance Optimizations

- Database connection pooling
- Efficient query optimization
- Caching for frequently accessed data
- Asynchronous processing for bulk operations
- Memory management for large datasets

## 🧪 Testing

### Manual Testing Checklist
- [ ] User authentication
- [ ] Prospect creation and editing
- [ ] Contact management
- [ ] Website data extraction
- [ ] LinkedIn data extraction
- [ ] AI script generation
- [ ] Script history and management
- [ ] Database operations
- [ ] Error handling scenarios

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the documentation
- Review the QUICKSTART.md file
- Open an issue on GitHub

## 🔄 Version History

### v2.0.0 (Current)
- Added comprehensive data extraction features
- Integrated OpenAI AI script generation
- Enhanced prospect management with auto-fill
- Improved UI/UX with component-based architecture
- Added bulk processing capabilities

### v1.0.0
- Initial release with basic prospect management
- User authentication system
- Database integration
- Basic CRUD operations 