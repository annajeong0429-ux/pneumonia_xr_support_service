from pathlib import Path

import torch
from PIL import Image
from torchvision import models, transforms

MODELS_DIR = Path(__file__).resolve().parent / "models"
NUM_FOLDS = 5
DEVICE = torch.device("cpu")
PNEUMONIA_INDEX = 1  # 출력 2개 클래스 중 인덱스 1 = 폐렴 (보고서 기준)

# 보고서에서 확인한 val/추론용 전처리: Resize((224,224)) -> ToTensor -> Normalize
_TRANSFORM = transforms.Compose([ transforms.Resize((224,224)), transforms.ToTensor(), transforms.Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])])


def _build_convnext_tiny() -> torch.nn.Module:
    model = models.convnext_tiny(weights=None)
    model.classifier[2] = torch.nn.Linear(model.classifier[2].in_features, 2)
    return model


def _build_densenet121() -> torch.nn.Module:
    model = models.densenet121(weights=None)
    model.classifier = torch.nn.Linear(model.classifier.in_features, 2)
    return model


def _load_fold_models(build_fn, filename_pattern: str) -> list[torch.nn.Module]:
    loaded = []
    for fold in range(1, NUM_FOLDS + 1):
        model = build_fn()
        state_dict = torch.load(
            MODELS_DIR / filename_pattern.format(fold=fold), map_location= DEVICE, weights_only= True)
        model.load_state_dict(state_dict)
        model.eval()
        loaded.append(model)
    return loaded


# 서버(모듈) 로드 시점에 한 번만 실행되어, 10개 모델이 메모리에 고정됨
print("[worker.model] 모델 로딩 중...")
CONVNEXT_MODELS = _load_fold_models(_build_convnext_tiny, "convnext_tiny_solo_fold{fold}.pth")
DENSENET_MODELS = _load_fold_models(_build_densenet121, "densenet121_fold{fold}.pth")
print(f"[worker.model] 로딩 완료 (ConvNeXt {len(CONVNEXT_MODELS)}fold, DenseNet {len(DENSENET_MODELS)}fold)")


def _preprocess(image: Image.Image) -> torch.Tensor:
    image = image.convert('RGB')
    tensor = _TRANSFORM(image)
    return tensor.unsqueeze(0)


def _predict_prob(fold_models: list[torch.nn.Module], input_tensor: torch.Tensor) -> float:
    probs = []
    with torch.no_grad():
        for model in fold_models: 
            logits = model(input_tensor)
            prob = torch.softmax(logits, dim=1)[0, PNEUMONIA_INDEX].item()
            probs.append(prob)
        return sum(probs) / len(probs)
    

def predict_pneumonia(image: Image.Image) -> dict:
    input_tensor = _preprocess(image)
    convnext_prob = _predict_prob(CONVNEXT_MODELS,input_tensor)
    densenet_prob = _predict_prob(DENSENET_MODELS, input_tensor)
    convnext_label = convnext_prob >= 0.5
    densenet_label = densenet_prob >= 0.5 
    is_pneumonia = convnext_label or densenet_label
    confidence = max(convnext_prob, densenet_prob)
    return {'is_pneumonia': is_pneumonia, 'confidence': round(confidence, 4), 'convnext_confidence': round(convnext_prob, 4),'densenet_confidence':round(densenet_prob, 4)}
