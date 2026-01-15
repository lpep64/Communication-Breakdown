# Contributing to Rapid-Response

Thank you for your interest in contributing to the Rapid-Response project! This guide will help you get started with development and contributions.

## Development Environment Setup

### Prerequisites

- **Python 3.10 or higher**
- **Node.js 16 or higher**
- **npm or yarn**
- **Git**

### Initial Setup

1. **Clone the repository:**
   ```powershell
   git clone https://github.com/URI-ISE/Rapid-Response.git
   cd Rapid-Response
   ```

2. **Choose an MVP to work on:**
   Each MVP is self-contained with its own backend and frontend.

3. **Backend Setup (Python/FastAPI):**
   ```powershell
   cd mvp#-name/backend
   python -m venv env
   .\env\Scripts\Activate.ps1  # Windows
   # source env/bin/activate    # macOS/Linux
   pip install -r requirements.txt
   ```

4. **Frontend Setup (React):**
   ```powershell
   cd mvp#-name/frontend
   npm install
   ```

## Running the Application

### Backend
```powershell
cd mvp#-name/backend
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`  
Interactive API docs at `http://localhost:8000/docs`

### Frontend
```powershell
cd mvp#-name/frontend
npm start
```

The React app will open at `http://localhost:3000`

## Code Style and Standards

### Python
- Follow PEP 8 style guidelines
- Use type hints where applicable
- Keep functions focused and modular
- Document complex logic with comments

### JavaScript/React
- Use functional components with hooks
- Follow React best practices
- Use meaningful variable and function names
- Keep components small and reusable

## Making Changes

### Workflow

1. **Create a new branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes:**
   - Write clean, well-documented code
   - Test your changes locally
   - Ensure backend and frontend both run without errors

3. **Commit your changes:**
   ```bash
   git add .
   git commit -m "Brief description of changes"
   ```

4. **Push to GitHub:**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create a Pull Request:**
   - Go to the repository on GitHub
   - Click "New Pull Request"
   - Select your branch
   - Fill out the PR template with details about your changes

## Pull Request Guidelines

- **Title:** Clear and descriptive title
- **Description:** Explain what changes you made and why
- **Testing:** Describe how you tested your changes
- **Screenshots:** Include screenshots for UI changes
- **Related Issues:** Reference any related issues with `#issue-number`

## Testing

While formal unit tests are not currently implemented, please ensure:

1. **Backend Testing:**
   - All API endpoints respond correctly
   - No Python errors or warnings
   - Test with sample data

2. **Frontend Testing:**
   - UI renders correctly in browser
   - All interactive elements work as expected
   - No console errors
   - Test responsive design on mobile/tablet

3. **Integration Testing:**
   - Backend and frontend communicate properly
   - Data flows correctly through the system
   - Test the complete user workflow

## Reporting Issues

When reporting bugs or issues, please include:

- **MVP affected:** Which MVP (1-4) has the issue
- **Description:** Clear description of the problem
- **Steps to reproduce:** How to recreate the issue
- **Expected behavior:** What should happen
- **Actual behavior:** What actually happens
- **Screenshots:** If applicable
- **Environment:** OS, Python version, Node version

## Feature Requests

We welcome feature suggestions! Please:

- Check existing issues to avoid duplicates
- Clearly describe the feature and its benefits
- Explain how it fits into the project goals
- Consider privacy and security implications

## Code of Conduct

- Be respectful and professional
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Respect different viewpoints and experiences

## Questions?

If you have questions about contributing:

- Open an issue with the `question` label
- Check existing documentation in the MVP-specific READMEs
- Review the main [README.md](./README.md) for project overview

---

Thank you for contributing to Rapid-Response! Your efforts help improve emergency personnel accountability systems.
