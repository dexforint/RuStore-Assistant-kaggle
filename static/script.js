// @ts-nocheck
const chat = document.getElementById("chat");
const chatInput = document.getElementById("chat-input");
const waitingTemplate = document.getElementById("waitingTemplate");
const serviceMessageTemplate = document.getElementById("serviceMessageTemplate");
const myMessageTemplate = document.getElementById("myMessageTemplate");
const uploadButton = document.getElementById("uploadButton");
const resetChatButton = document.getElementById("resetChatButton");

const IP = document.getElementById("ip").innerHTML.trim();

// chat.innerHTML = localStorage.getItem("chat");
// localStorage.setItem("chat", chat.innerHTML);

function auto_grow(event) {
	chatInput.style.height = "5px";
	chatInput.style.height = chatInput.scrollHeight + "px";
}
chatInput.addEventListener("input", auto_grow);

chat.scrollTop = chat.scrollHeight;
let iCanSendMessage = true;

function addWaiting() {
	const clone = document.importNode(waitingTemplate.content, true);
	chat.appendChild(clone);
}

function removeWaiting() {
	let elements = chat.getElementsByClassName("loading-indicator");

	for (var i = elements.length - 1; i >= 0; i--) {
		elements[i].parentNode.removeChild(elements[i]);
	}
}

async function textRequest(text) {
	let result;
	try {
		const response = await fetch(`http://${IP}:8000/query`, {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
			body: JSON.stringify({ query: text }),
		});

		if (response.ok) {
			result = await response.json();
		} else {
			result = {
				error: "Ошибка запроса!",
			};
		}
	} catch (error) {
		result = {
			error: "Неизвестная ошибка!",
		};
	}

	return result;
}

var tagsToReplace = {
	"&": "&amp;",
	"<": "&lt;",
	">": "&gt;",
};

function replaceTag(tag) {
	return tagsToReplace[tag] || tag;
}

function sendServiceMessage(response) {
	if (response["error"]) {
		let serviceMessage = document.importNode(serviceErrorTemplate.content, true);
		let text = response["error"].replace(/\n/g, "<br/>", "g");
		serviceMessage.querySelector(".chat-service-text").innerHTML = text;
		serviceMessage.querySelector(".chat-service-title").textContent = "Error"; // response["from"];

		removeWaiting();
		chat.append(serviceMessage);
	} else {
		let serviceMessage = document.importNode(serviceMessageTemplate.content, true);
		let text = response["answer"].replace(/\n/g, "<br/>", "g");
		serviceMessage.querySelector(".chat-service-text").innerHTML = text;
		serviceMessage.querySelector(".chat-service-title").textContent = "RuStore Assistant"; // response["from"];

		removeWaiting();
		chat.append(serviceMessage);
	}
}

async function sendMyMessage(text) {
	text = text.trim();
	text = text.replace(/[&<>]/g, replaceTag);
	text = text.replace(/\n/g, "<br/>", "g");
	const clone = document.importNode(myMessageTemplate.content, true);
	clone.querySelector(".chat-my-text").innerHTML = text;
	chat.appendChild(clone);
	iCanSendMessage = false;

	setTimeout(function () {
		chatInput.value = "";
	}, 20);

	addWaiting();
	chat.scrollTop = chat.scrollHeight;

	let response = await textRequest(text);
	console.log(response);

	sendServiceMessage(response);
}

chatInput.addEventListener("keydown", function (event) {
	let value = chatInput.value.trim();

	if (event.key === "Enter") {
		if (!event.shiftKey) {
			if (value.length > 4 && iCanSendMessage == true) sendMyMessage(value);
			setTimeout(() => {
				auto_grow(event);
			}, 30);
			event.preventDefault();
			return false;
		}
	}
});

const downloadBtn = document.getElementById("download-btn");

document.addEventListener("click", (event) => {
	let target = event.target;
	let downloadadBtn = target.closest(".download-btn");

	if (!downloadadBtn) return;

	const fileUrl = downloadadBtn.dataset.fileurl; // URL файла на сервере
	const fileUrlSplit = fileUrl.split("/");
	const fileName = fileUrlSplit[fileUrlSplit.length - 1];

	const xhr = new XMLHttpRequest();
	xhr.open("GET", fileUrl, true);
	xhr.responseType = "blob";

	xhr.onload = function () {
		if (xhr.status === 200) {
			const blob = new Blob([xhr.response], { type: "text/plain" });
			const url = URL.createObjectURL(blob);
			const a = document.createElement("a");
			a.href = url;
			a.download = fileName;
			a.click();
			URL.revokeObjectURL(url);
		} else {
			console.error("Ошибка загрузки файла:", xhr.statusText);
		}
	};

	xhr.send();
});

resetChatButton.addEventListener("click", function (event) {
	fetch(`http://${IP}:8000/reset_history`, {
		method: "POST",
		headers: {
			"Content-Type": "text/plain",
		},
	})
		.then((response) => response.json())
		.then((response) => {
			if (!response.error) {
				// localStorage.removeItem("chat");
				chat.innerHTML = `
                <div class="chat-service-message-container">
                    <div class="chat-service-message">
                        <h2 class="chat-service-title">RuStore Bot</h2>
                        <p class="chat-service-text">
                            Привет! Я являюсь Универсальным Помощником по документации RuStore! Если у вас возникли
                            вопросы, пожалуйста, задайте мне их и я отвечу!

                        </p>
                    </div>
                </div>`;
			}
		})
		.catch((error) => {
			console.error("Ошибка:", error);
		});
});

// ! Бегущая строка
// Напиши код на HTML, CSS, Javascript для создания трёх бесконечных бегущих горизонтальных строк из набора изображений (для каждой строки разный набор изображений), состоящей из изображений 72x72px с отступами от друг друга 12px. Эти строки должны идти справа налево с разной скоростью каждая. Отступ между строками 24px. В каждой горизонтальной строке не должно быть пустых простанств, даже если изображений не хватает, чтобы заполнить всю ширину экрана. Бегущая строка должна быть плавной и без резких смещений.
const images1 = [
	"/static/companies_1/2_GIS.png",
	"/static/companies_1/Blink.png",
	"/static/companies_1/gosuslugi.png",
	"/static/companies_1/mir.png",
	"/static/companies_1/ozon.png",
	"/static/companies_1/pochta_mail.png",
	"/static/companies_1/vk_video.png",
	"/static/companies_1/yandex_browser.png",
];
const images2 = [
	"/static/companies_2/alfa_bank.png",
	"/static/companies_2/okko.png",
	"/static/companies_2/sber.png",
	"/static/companies_2/Sber_Market.png",
	"/static/companies_2/tinkoff.png",
	"/static/companies_2/VK_znakomstva.png",
	"/static/companies_2/wink.png",
	"/static/companies_2/yula.png",
];

const images3 = [
	"/static/companies_3/avito.png",
	"/static/companies_3/Lenta.png",
	"/static/companies_3/mts.png",
	"/static/companies_3/odnoklassniki.png",
	"/static/companies_3/Tanks.png",
	"/static/companies_3/wildberries.png",
	"/static/companies_3/yandex_karti.png",
	"/static/companies_3/yandex_market.png",
];

function createMarquee(containerId, images, speed) {
	const container = document.getElementById(containerId);
	const marqueeContent = document.createElement("div");
	marqueeContent.style.display = "flex";
	marqueeContent.style.animation = `marquee ${speed}s linear infinite`;

	// Заполняем контейнер изображениями
	const fillContainer = () => {
		for (let img of images) {
			const imgElement = document.createElement("img");
			imgElement.src = img;
			marqueeContent.appendChild(imgElement);
		}
	};

	// Заполняем контейнер дважды для плавной анимации
	for (let i = 0; i < 10; i++) {
		fillContainer();
	}

	container.appendChild(marqueeContent);
}

createMarquee("marquee1", images1, 15);
createMarquee("marquee2", images2, 12);
createMarquee("marquee3", images3, 10);

// Добавляем keyframes для анимации
const style = document.createElement("style");
style.textContent = `
    @keyframes marquee {
        0% { transform: translateX(0%); }
        100% { transform: translateX(-30%); }
    }
`;
document.head.appendChild(style);

// !Record
let mediaRecorder;
let audioChunks = [];

const startRecordingButton = document.getElementById("recordButton");

startRecordingButton.addEventListener("click", clickRecording);
let isRecording = false;

async function clickRecording() {
	if (isRecording) {
		await stopRecording();
		startRecordingButton.style.backgroundColor = "";
		isRecording = false;
	} else {
		await startRecording();
		startRecordingButton.style.backgroundColor = "red";
		isRecording = true;
	}
}

async function startRecording() {
	const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
	mediaRecorder = new MediaRecorder(stream);

	mediaRecorder.addEventListener("dataavailable", (event) => {
		audioChunks.push(event.data);
	});

	mediaRecorder.start();
	// startRecordingButton.disabled = true;
	// stopRecordingButton.disabled = false;
	console.log("Recording...");
}

function stopRecording() {
	mediaRecorder.stop();
	// startRecordingButton.disabled = false;
	// stopRecordingButton.disabled = true;
	console.log("Recording stopped. Sending to server...");

	mediaRecorder.addEventListener("stop", () => {
		const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
		sendAudioToServer(audioBlob);
		audioChunks = [];
	});
}

async function sendAudioToServer(audioBlob) {
	const formData = new FormData();
	formData.append("audio", audioBlob, "recording.webm");

	try {
		const response = await fetch(`http://${IP}:8000/upload_audio`, {
			method: "POST",
			body: formData,
		});

		if (response.ok) {
			console.log("Audio sent successfully!");
		} else {
			console.log("Error sending audio to server.");
		}
	} catch (error) {
		console.error("Error:", error);
	}
}

async function uploadImage(files) {
	const file = files[0];

	if (!file) {
		console.log("Please select an image file");
		return;
	}

	const formData = new FormData();
	formData.append("image", file);

	try {
		const response = await fetch(`http://${IP}:8000/upload_image`, {
			method: "POST",
			body: formData,
		});

		const result = await response.json();
		console.error("result:", result);
	} catch (error) {
		console.log("Error:", error);
	}
}
