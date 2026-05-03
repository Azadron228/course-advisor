# Design Doc: Full Localization and Kazakh Support

## 1. Goal
The objective is to achieve "full localization" by moving all hardcoded strings to translation files, updating specific Russian translations as requested, removing obsolete localization keys, and adding support for the Kazakh (kk) language.

## 2. Proposed Changes

### 2.1. Translation File Updates
- **`frontend/messages/en.json`**:
  - Add `validation.goalMinLength`: "Goal must be at least 5 characters".
  - Remove obsolete keys under `Plan`: `beginner`, `intermediate`, `advanced`, `learningStyle`, `studyTime`, `beginnerLevel`, `intermediateLevel`, `advancedLevel`, `visual`, `practical`, `theoretical`.
- **`frontend/messages/ru.json`**:
  - Update `Plan.myPaths` to `"Мои планы обучения"`.
  - Add `validation.goalMinLength`: "Цель должна содержать не менее 5 символов".
  - Remove the same obsolete keys as in `en.json`.
- **`frontend/messages/kk.json` (New)**:
  - Provide complete Kazakh translations for all existing keys.

### 2.2. Kazakh Language Integration
- **`frontend/src/i18n/routing.ts`**: Add `'kk'` to the `locales` array.
- **`frontend/src/middleware.ts`**: Update the locale detection regex and logic to include the `kk` segment.
- **`frontend/src/components/shared/language-switcher.tsx`**: Add the Kazakh option `{ code: 'kk', label: 'Қазақша' }` to the `LOCALES` list.

### 2.3. Hardcoded String Localization
- **`frontend/src/components/features/learning-plan-generator.tsx`**:
  - Update the Zod schema for `goal` to use a dynamic translation for the minimum length error message.
  - *Note: Since Zod schemas are often defined outside the component, I will ensure the translation is either passed in or the schema is defined within the component where `useTranslations` is available, or use `next-intl`'s recommended pattern for Zod.*

## 3. Kazakh Translations (kk.json)
```json
{
  "Common": {
    "title": "EduPath AI",
    "searchPlaceholder": "Курстарды, дағдыларды іздеу...",
    "logout": "Шығу",
    "profile": "Менің профилім",
    "settings": "Баптаулар",
    "loading": "Жүктелуде...",
    "saveChanges": "Өзгерістерді сақтау",
    "savingChanges": "Өзгерістер сақталуда...",
    "beta": "Бета",
    "aiPowered": "ИИ негізінде",
    "navHub": "Навигация",
    "adminPortal": "Админ панелі",
    "backToDashboard": "Басқару панеліне оралу",
    "go": "Өту",
    "thinking": "Ойлануда...",
    "error": "Қате орын алды"
  },
  "Auth": {
    "login": "Кіру",
    "register": "Тіркелу",
    "signIn": "Кіру",
    "signUp": "Тіркелу",
    "createAccount": "Аккаунт жасау",
    "registerSubtitle": "ИИ негізіндегі жеке оқыту жоспарларымен жолыңызды бастаңыз",
    "welcomeBack": "Қайта қош келдіңіз",
    "continueJourney": "Оқу жолыңызды жалғастырыңыз",
    "emailAddress": "Электрондық пошта",
    "password": "Құпия сөз",
    "forgotPassword": "Құпия сөзді ұмыттыңыз ба?",
    "dontHaveAccount": "Аккаунтыңыз жоқ па?",
    "alreadyHaveAccount": "Аккаунтыңыз бар ма?",
    "signingIn": "Кіруде...",
    "creatingAccount": "Аккаунт жасалуда...",
    "userProfile": "Пайдаланушы профилі",
    "manageProfile": "Жеке ақпаратыңызды және мансаптық мақсаттарыңызды басқарыңыз",
    "fullName": "Толық аты-жөні",
    "careerGoal": "Мансаптық мақсат",
    "careerGoalPlaceholder": "мыс., React-ке маманданған аға фронтенд-инженер болу",
    "profileUpdated": "Профиль сәтті жаңартылды!",
    "profileUpdateError": "Профильді жаңарту мүмкін болмады. Қайталап көріңіз.",
    "loginError": "Электрондық пошта немесе құпия сөз қате. Қайталап көріңіз.",
    "nameMinLength": "Аты кемінде 2 таңбадан тұруы керек",
    "invalidEmail": "Электрондық пошта мекенжайы қате",
    "goalMinLength": "Мақсат кемінде 5 таңбадан тұруы керек"
  },
  "Dashboard": {
    "activePlan": "Белсенді оқу жоспары",
    "noActivePlan": "Белсенді жоспар жоқ",
    "progress": "Прогресс",
    "subtitle": "Прогресіңізді қадағалаңыз және оқу жолыңызды жалғастырыңыз.",
    "achievementLevel": "Жетістік деңгейі",
    "risingStar": "Жас жұлдыз",
    "achievementDesc": "Жаңа белгілерді ашу және дағдыларыңызды арттыру үшін тапсырмаларды орындауды жалғастырыңыз!",
    "learningPlanDesc": "Құрылымдалған оқу жолыңызды жалғастырыңыз және күнделікті мақсаттарды қадағалаңыз.",
    "aiAdvisorDesc": "Кеңес пен көмек алу үшін жеке көмекшімен сөйлесіңіз.",
    "goTo": "Өту",
    "insightsSoon": "Дағдылар аналитикасы жақын арада болады",
    "insightsDesc": "Оқу процесінің кеңейтілген аналитикасы.",
    "leaderboards": "Көшбасшылар тақтасы",
    "leaderboardsDesc": "Өз салаңыздағы басқа білім алушылармен бәсекелесіңіз.",
    "quickActions": "Жылдам әрекеттер",
    "quickActionsDesc": "Соңғы сабақты бір басумен жалғастырыңыз."
  },
  "Chat": {
    "title": "ИИ Кеңесші",
    "subtitle": "Жеке кеңестер мен курс ұсыныстарын алыңыз",
    "companion": "Сіздің жеке оқу көмекшіңіз",
    "howCanIHelp": "Бүгін сізге қалай көмектесе аламын?",
    "intro": "Маған курстар туралы, дағдыларды дамыту немесе мансаптық мақсаттарыңызға қалай жетуге болатыны туралы сұрақтар қойыңыз.",
    "suggestPython": "Python курстарын ұсын",
    "suggestWebDev": "Web-әзірлеу үшін қандай дағдылар қажет?",
    "suggestPlan": "Менің оқу жоспарымды түсіндір",
    "suggestDataScience": "Data Science-ті қалай бастауға болады?",
    "placeholder": "Кеңесшіден кез келген нәрсені сұраңыз...",
    "aiPoweredNote": "Профиліңіз бен мақсаттарыңызға негізделген ИИ ұсыныстары.",
    "clearHistory": "Тарихты тазалау",
    "newChat": "Жаңа чат",
    "noHistory": "Чат тарихы әлі жоқ"
  },
  "Plan": {
    "myPaths": "Менің оқу жоспарларым",
    "noPaths": "Жоспарлар әлі жоқ",
    "startGenerating": "Алғашқы жеке оқу жоспарыңызды жасаудан бастаңыз.",
    "createNew": "Жаңа жоспар жасау",
    "defineGoals": "Мақсаттарыңыз бен оқу талғамдарыңызды анықтаңыз.",
    "goalLabel": "Сіздің мақсатыңыз қандай?",
    "goalPlaceholder": "мыс., React және ИИ-ге бағытталған аға фронтенд-инженер болу.",
    "interestsLabel": "Қызығушылықтар және нақты тақырыптар",
    "skillLevelLabel": "Ағымдағы дағды деңгейі",
    "transcriptNote": "ИИ бұрын аяқтаған курстарды өткізіп жіберуі үшін транскрипцияңызды (.html) жүктеңіз.",
    "clickToUpload": "Транскрипцияны жүктеу үшін басыңыз",
    "supportsHtml": ".HTML қолданады",
    "myPlan": "Менің оқу жоспарым",
    "notFound": "Оқу жоспары табылмады. Оны жасау үшін басқару панеліне өтіңіз.",
    "materials": "Курс материалдары",
    "noMaterials": "Бұл курс үшін әлі арнайы материалдар берілмеген.",
    "learningStyle": "Оқу стилі",
    "studyTime": "Оқу уақыты (сағат/апта)",
    "academicTranscript": "Академиялық транскрипт (міндетті емес)",
    "generateButton": "Оқу жоспарымды жасау",
    "drafting": "ИИ жоспарыңызды жасауда...",
    "typeAndPressEnter": "Жазыңыз және Enter басыңыз",
    "removeFile": "Файлды жою",
    "getStarted": "Бастау",
    "stepsCount": "{count} қадам",
    "hoursPerWeek": "{count}сағ/апта",
    "goalValue": "Мақсат: {goal}",
    "stepLabel": "Қадам {index}",
    "external": "Сыртқы",
    "markComplete": "Аяқталды деп белгілеу",
    "updating": "Жаңартылуда...",
    "openExternal": "Сыртқы ресурсты ашу",
    "viewMaterials": "Материалдарды қарау",
    "loadingMaterials": "Материалдар жүктелуде...",
    "loadError": "Курс материалдарын жүктеу мүмкін болмады"
  },
  "Navigation": {
    "dashboard": "Басқару панелі",
    "learningPlan": "Оқу жоспары",
    "aiAdvisor": "ИИ Кеңесші",
    "profile": "Профиль"
  },
  "Admin": {
    "courseManagement": "Курстарды басқару",
    "manageCoursesDesc": "Каталогтағы курстарды жасаңыз, өңдеңіз және басқарыңыз.",
    "addNewCourse": "Жаңа курс қосу",
    "editCourse": "Курсты өңдеу",
    "deleteCourse": "Курсты жою",
    "noCoursesFound": "Курстар табылмады",
    "startFirstCourse": "Алғашқы курсыңызды жасаудан бастаңыз.",
    "confirmDelete": "\"{name}\" курсын жоюды қалайтыныңызға сенімдісіз бе?",
    "deleteError": "Курсты жою мүмкін болмады. Қайталап көріңіз.",
    "generalInfo": "Жалпы ақпарат",
    "metadataSkills": "Метадеректер және дағдылар",
    "subjectName": "Пән атауы",
    "description": "Сипаттама",
    "skillsTaught": "Оқытылатын дағдылар (үтір арқылы)",
    "skillsPlaceholder": "React, TypeScript, Testing...",
    "updateCourse": "Курсты жаңарту",
    "createCourse": "Курс жасау",
    "backToCourses": "Курстарға оралу",
    "eduMaterials": "Оқу материалдары",
    "syllabusAnalyzed": "Силлабус RAG ұсыныстары үшін талданды",
    "uploadPrompt": "ИИ ұсыныстарын жақсарту үшін PDF/Txt жүктеңіз",
    "uploading": "Жүктелуде...",
    "processing": "Өңделуде...",
    "uploadFile": "Файлды жүктеу",
    "createSuccess": "Курс сәтті жасалды!",
    "updateSuccess": "Курс сәтті жаңартылды!",
    "uploadSuccess": "Материалдар сәтті жүктелді!"
  }
}
```

## 4. Verification Plan
- **Language Switcher**: Check that 'EN', 'RU', and 'KK' options are available and functional.
- **Plan Page (RU)**: Verify heading is "Мои планы обучения".
- **Plan Page (KK)**: Verify heading is "Менің оқу жоспарларым" and all other elements are translated.
- **Validation**: Trigger the goal validation error and ensure it shows translated messages in all three languages.
- **Cleanup**: Verify that the removed keys are no longer present in JSON files and that the application still runs without errors.
