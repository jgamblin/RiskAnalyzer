let cves = [];
let currentCveIndex = 0;
let correctAnswers = 0;
let totalQuestions = 0;
let currentQuestionType = '';
let hintCount = 2;
const maxQuestions = 20;

const url = 'https://game.cve.icu/cves.csv';

fetch(url, {
    method: 'GET',
})
    .then(response => response.text())
    .then(data => {
        cves = parseCsv(data);
        askQuestionType();
    });

function parseCsv(data) {
    const lines = data.split('\n').filter(line => line.trim() !== '');
    const headers = lines[0].split(',').map(header => header.trim());
    return lines.slice(1).map(line => {
        const values = line.split(',').map(value => value.trim());
        let cve = {};
        headers.forEach((header, index) => {
            cve[header] = values[index];
        });
        return cve;
    });
}

function askQuestionType() {
    document.getElementById('question-container').style.display = 'none';
    document.getElementById('skip-button').style.display = 'none';
    document.getElementById('hint-button').style.display = 'none';
    document.getElementById('score').style.display = 'none';
    const questionTypeContainer = document.getElementById('question-type-container');
    questionTypeContainer.innerHTML = `
        <p>Do you want to guess CVSS Base Scores or CWEs?</p>
        <button id="cvss-button" class="game-button">CVSS Base Scores</button>
        <button id="cwe-button" class="game-button">CWEs</button>
    `;
    document.getElementById('cvss-button').onclick = () => startGame('CVSS3_BaseScore');
    document.getElementById('cwe-button').onclick = () => startGame('CWE');
}

function startGame(questionType) {
    currentQuestionType = questionType;
    document.getElementById('question-type-container').innerHTML = '';
    document.getElementById('question-container').style.display = 'block';
    document.getElementById('skip-button').style.display = 'inline-block';
    document.getElementById('hint-button').style.display = 'inline-block';
    document.getElementById('score').style.display = 'block';
    displayCve();
    updateScoreboard();
}

function displayCve() {
    if (totalQuestions >= maxQuestions) {
        endGame();
        return;
    }
    const cve = cves[currentCveIndex];
    document.getElementById('cve-id').innerText = cve.CVE;
    document.getElementById('cve-description').innerText = cve.Description;
    const choicesContainer = document.getElementById('choices-container');
    choicesContainer.innerHTML = '';
    const questionText = currentQuestionType === 'CVSS3_BaseScore' ? 'What is this CVE\'s CVSS 3 Base Score?' : 'What is this CVE\'s CWE?';
    document.getElementById('question').innerText = questionText;
    const choices = generateChoices(cve);
    choices.forEach(choice => {
        const button = document.createElement('button');
        button.className = 'choice';
        button.innerText = choice;
        button.onclick = () => checkAnswer(choice, cve);
        choicesContainer.appendChild(button);
    });
    document.getElementById('answer').innerText = '';
}

function generateChoices(cve) {
    const correctChoice = cve[currentQuestionType];
    const choices = [correctChoice];
    while (choices.length < 4) {
        const randomChoice = currentQuestionType === 'CVSS3_BaseScore' ? (Math.random() * 8 + 2).toFixed(1) : `CWE-${Math.floor(Math.random() * 1000)}`;
        if (!choices.includes(randomChoice) && (currentQuestionType === 'CWE' || !randomChoice.startsWith('CWE-'))) {
            choices.push(randomChoice);
        }
    }
    return choices.sort(() => Math.random() - 0.5);
}

function checkAnswer(choice, cve) {
    totalQuestions++;
    let resultText;
    const cveLink = `<a href="https://nvd.nist.gov/vuln/detail/${cve.CVE}" target="_blank">${cve.CVE}</a>`;
    if (currentQuestionType === 'CWE') {
        const cweLink = `<a href="https://cwe.mitre.org/data/definitions/${cve.CWE.split('-')[1]}.html" target="_blank">${cve.CWE}</a>`;
        if (choice == cve[currentQuestionType]) {
            correctAnswers++;
            resultText = `<strong>Correct!</strong> The correct answer for ${cveLink} is ${cweLink}.`;
        } else {
            resultText = `<strong>Wrong!</strong> The correct answer for ${cveLink} is ${cweLink}.`;
        }
    } else {
        if (choice == cve[currentQuestionType]) {
            correctAnswers++;
            resultText = `<strong>Correct!</strong> The correct answer for ${cveLink} is ${cve[currentQuestionType]}.`;
        } else {
            resultText = `<strong>Wrong!</strong> The correct answer for ${cveLink} is ${cve[currentQuestionType]}.`;
        }
    }
    document.getElementById('last-result').innerHTML = resultText;
    updateScoreboard();
    currentCveIndex = (currentCveIndex + 1) % cves.length;
    displayCve();
}

function updateScoreboard() {
    const score = document.getElementById('score');
    const percentage = totalQuestions === 0 ? 100 : ((correctAnswers / totalQuestions) * 100).toFixed(2);
    score.innerText = `Score: ${correctAnswers} / ${totalQuestions} (${percentage}%)`;
}

function useHint() {
    if (hintCount > 0) {
        hintCount--;
        const choicesContainer = document.getElementById('choices-container');
        const buttons = Array.from(choicesContainer.getElementsByClassName('choice'));
        const correctChoice = cves[currentCveIndex][currentQuestionType];
        let removed = 0;
        buttons.forEach(button => {
            if (button.innerText !== correctChoice && removed < 2) {
                button.style.display = 'none';
                removed++;
            }
        });
    } else {
        document.getElementById('answer').innerText = 'No hints left!';
    }
}

function nextQuestion() {
    totalQuestions++;
    const cve = cves[currentCveIndex];
    const cveLink = `<a href="https://nvd.nist.gov/vuln/detail/${cve.CVE}" target="_blank">${cve.CVE}</a>`;
    let resultText;
    if (currentQuestionType === 'CWE') {
        const cweLink = `<a href="https://cwe.mitre.org/data/definitions/${cve.CWE.split('-')[1]}.html" target="_blank">${cve.CWE}</a>`;
        resultText = `<strong>Wrong!</strong> The correct answer for ${cveLink} is ${cweLink}.`;
    } else {
        resultText = `<strong>Wrong!</strong> The correct answer for ${cveLink} is ${cve[currentQuestionType]}.`;
    }
    document.getElementById('last-result').innerHTML = resultText;
    updateScoreboard();
    currentCveIndex = (currentCveIndex + 1) % cves.length;
    displayCve();
}

function endGame() {
    document.getElementById('question-container').style.display = 'none';
    document.getElementById('skip-button').style.display = 'none';
    document.getElementById('hint-button').style.display = 'none';
    document.getElementById('score').style.display = 'none';
    document.getElementById('last-result').innerHTML = ''; // Clear the last result
    const questionTypeContainer = document.getElementById('question-type-container');
    questionTypeContainer.innerHTML = `
        <p>Game Over! You got ${correctAnswers} out of ${maxQuestions} questions right.</p>
        <p>Do you want to play again?</p>
        <button id="cvss-button" class="game-button">CVSS Base Scores</button>
        <button id="cwe-button" class="game-button">CWEs</button>
    `;
    document.getElementById('cvss-button').onclick = () => startNewGame('CVSS3_BaseScore');
    document.getElementById('cwe-button').onclick = () => startNewGame('CWE');
}

function startNewGame(questionType) {
    correctAnswers = 0;
    totalQuestions = 0;
    hintCount = 2;
    currentQuestionType = questionType;
    document.getElementById('question-type-container').innerHTML = ''; // Hide the game selector
    document.getElementById('skip-button').disabled = false;
    document.getElementById('hint-button').disabled = false;
    document.getElementById('question-container').innerHTML = `
        <div class="info-box">
            <p><strong>CVE ID:</strong> <span id="cve-id"></span></p>
            <p><strong>Description:</strong> <span id="cve-description"></span></p>
        </div>
        <p id="question" class="bold"></p>
        <div id="choices-container"></div>
    `;
    document.getElementById('question-container').style.display = 'block';
    document.getElementById('skip-button').style.display = 'inline-block';
    document.getElementById('hint-button').style.display = 'inline-block';
    document.getElementById('score').style.display = 'block';
    displayCve();
    updateScoreboard();
}

document.getElementById('skip-button').onclick = nextQuestion;
document.getElementById('hint-button').onclick = useHint;
