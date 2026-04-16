# Design Spec: AI Chat and Dashboard Layout Refactor

This document outlines the design for integrating a persistent AI assistant into the Course Advisor dashboard and refactoring the layout to improve user experience.

## 1. Problem Statement
The current dashboard puts transcript upload and parameter settings (difficulty, workload) in the sidebar, which is a "one-off" interaction. This space could be better utilized for a continuous AI advisor that helps students with academic and career decisions.

## 2. Proposed Changes

### 2.1 Frontend Refactor (Dashboard)
- **Sidebar Transformation:**
  - The sidebar will now host a **Chat Interface**.
  - A message list will display the conversation history.
  - A sticky input field at the bottom for user queries.
  - **Settings Drawer:** A small, collapsible section at the top of the sidebar for "Academic Preferences" (Difficulty, Workload sliders, and Interests tags).
- **Main Content Area:**
  - **Getting Started Card:** When no transcript is uploaded, the main area will display a large, friendly card with the transcript upload zone.
  - **Roadmap Display:** Once the transcript is processed, the existing Learning Path and Recommended Courses will be displayed as usual.

### 2.2 Backend AI Chat
- **Redis-Backed History:**
  - Chat history will be stored in Redis to provide persistence across sessions without heavy database overhead.
  - Key: `chat_history:{user_id}`.
  - Value: JSON-serialized list of messages.
  - Retention: Last 20-30 messages.
- **New API Endpoints:**
  - `POST /api/v1/recommendations/chat`: Processes a user message.
    - Retrieves history from Redis.
    - Constructs a system prompt including the student's academic profile (parsed from transcript if available).
    - Calls the LLM via `get_model`.
    - Saves the interaction back to Redis.
  - `GET /api/v1/recommendations/chat/history`: Returns the current conversation for the user.
  - `DELETE /api/v1/recommendations/chat/history`: Clears the chat context.

## 3. Architecture & Data Flow

### 3.1 Chat Flow
1. User types a message in the Sidebar.
2. Frontend sends message to `POST /chat`.
3. Backend:
   - Fetches User's transcript/skills from PostgreSQL (if they exist).
   - Fetches Chat History from Redis.
   - Merges these into an LLM prompt.
   - LLM generates a response.
   - Backend saves User Message + Assistant Response to Redis.
4. Frontend updates the message list.

### 3.2 Layout Logic
- `const [hasData, setHasData] = useState(false);`
- If `!hasData`, show `UploadComponent` in the main view.
- If `hasData`, show `RoadmapComponent` in the main view.

## 4. Technical Details

### 4.1 Redis Key Management
We will use the user's email or database ID as the unique identifier for Redis keys.

### 4.2 LLM System Prompt
```text
You are an expert Academic Advisor for university students. 
You have access to the student's academic profile: {student_profile}.
Use this context to provide personalized advice on courses, careers, and learning strategies.
Be encouraging, professional, and concise.
```

## 5. Verification Plan
- **Unit Tests:** Test the Redis history service (save/retrieve/limit).
- **Integration Tests:** Verify the `/chat` endpoint responds correctly with context.
- **UI Tests:** Ensure the transcript upload still triggers roadmap generation and that the sidebar remains functional for chat.
