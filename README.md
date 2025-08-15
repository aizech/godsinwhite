<img src="assets/godsinwhite_team.png" alt="" width="400"/>

# GodsinWhite

Gods in White is your personal gateway to advanced medical diagnostics—powered by AI and backed by real medical expertise. Designed for patients, healthcare professionals, and curious minds alike, this app transforms how medical images are analyzed and understood.

# Corpus Analytica - Your Trusted Partner in Healthcare

At [Corpus Analytica](https://www.corpusanalytica.com), we redefine how medical professionals and patients connect—through a platform built for simplicity, security, and global reach.

#### What We Offer:
- Seamless Connections: We unite doctors, specialists, and patients through our cutting-edge digital platform.

- Expert Second Opinions: Gain easy access to a network of certified physicians and specialists for reliable second opinions.

- Effortless Booking: Our intuitive interface makes requesting and scheduling consultations fast and frustration-free.

- Global Access: Wherever you are, our online consultations bring expert medical advice right to your screen.

- Data You Can Trust: We uphold the highest standards in data protection and patient privacy—because your health deserves nothing less.

#### Experience Healthcare in a New Dimension
Your health is invaluable. With Corpus Analytica, discover a smarter, safer, and more connected way to care.

> *"Healthcare should be accessible, transparent, and empowering. At Corpus Analytica, we're building more than just a platform—we're building trust, one consultation at a time."* — Bernhard Z., Founder of [Corpus Analytica](https://www.corpusanalytica.com)


## Live Demo

Take a look at the [live demo here](https://godsinwhite.streamlit.app/)


## Features

- 🏥 **Medical AI Focus**: Specialized agents and tools designed for healthcare applications
- 🤖 **Multi-Agent Orchestration**: Coordinate multiple medical AI agents through a single interface
- 🧠 **Medical Knowledge Integration**: Access and utilize extensive medical knowledge bases
- 🔬 **Clinical Tools**: Integration with medical software and healthcare systems
- 📊 **Healthcare Analytics**: Advanced data processing and medical insights
- 💾 **Secure Session Management**: HIPAA-compliant conversation and data storage
- 🎨 **Intuitive Medical UI**: Clean, responsive interface designed for healthcare professionals
- 🤝 **Collaborative Care**: Enable seamless communication between different medical AI agents

## System Requirements

- Python 3.8 or higher
- Git (for cloning the repository)
- Internet connection for API access

## Installation

1. **Clone the Repository**

```bash
git clone https://github.com/aizech/godsinwhite.git
cd godsinwhite
```

2. **Set Up Virtual Environment**

Using venv (recommended):
```bash
python -m venv venv
# On Windows
.\venv\Scripts\activate
# On Unix or MacOS
source venv/bin/activate
```

3. **Install Dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure Environment Variables**

**Important:** In the configuration page you can bring your own API keys.

Alternatively, you can create a `.env` file in the project root and configure your API keys:

```env
OPENAI_API_KEY=your_openai_key
```

5. **Launch the Application**

```bash
streamlit run Home.py
```

The application will be available at `http://localhost:8501` by default.

## Project Structure

```
├── Home.py              # Main Streamlit application entry point
├── agents/              # Agent definitions and configurations
├── pages/              # Additional Streamlit pages
├── tools/              # Custom tool implementations
├── knowledge_docs/     # Knowledge base documents
├── assets/             # Static assets (images, icons)
├── config.py          # Application configuration
└── utils.py           # Utility functions
```

## Configuration

The application can be configured through:

- `.env` file for API keys and sensitive data
- `config.py` for application settings
- `presets.json` for agent presets and configurations

## Example Use Cases

1. **Medical Knowledge Assistance**
   - "What are the latest treatment guidelines for condition X?"
   - "Explain the differential diagnosis for these symptoms"
   - "Summarize recent research on this treatment method"

2. **Clinical Decision Support**
   - "Analyze these lab results and suggest possible diagnoses"
   - "Review this patient's history for potential drug interactions"
   - "Generate a preliminary assessment based on these symptoms"

3. **Healthcare Research**
   - "Find recent clinical trials related to this condition"
   - "Analyze treatment outcomes across different patient groups"
   - "Summarize the latest research in this medical field"

4. **Medical Documentation**
   - "Help structure this clinical note"
   - "Generate a template for this type of medical report"
   - "Assist in coding this medical procedure"

## Support

For support and questions:
- Open an issue in the GitHub repository
- Check the documentation in the `knowledge_docs` directory
- Join our community discussions

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Based on the HALO framework for multi-agent orchestration
- Powered by various AI models and APIs

The application uses SQLite for session storage (`halo_sessions.db`), so no external database setup (like PgVector or Qdrant) is needed for basic operation.

Open [localhost:8501](http://localhost:8501) to view your GodsinWhite interface.