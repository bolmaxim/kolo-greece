using Kolo.CameraSystem;
using Kolo.Input;
using Kolo.Interactables;
using Kolo.Player;
using Kolo.UI;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem.UI;
using UnityEngine.SceneManagement;
using UnityEngine.UI;

namespace Kolo.Level
{
    [DisallowMultipleComponent]
    public sealed class MeteoraSliceBuilder : MonoBehaviour
    {
        private static Sprite whiteSprite;

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void CreateForSlice()
        {
            if (SceneManager.GetActiveScene().name != "MeteoraSlice"
                || FindAnyObjectByType<MeteoraSliceBuilder>() != null)
            {
                return;
            }

            new GameObject("Meteora Slice Builder")
                .AddComponent<MeteoraSliceBuilder>()
                .Build();
        }

        public void Build()
        {
            if (GameObject.Find("Kolo") != null)
            {
                return;
            }

            CreateBackground();

            LevelFlowController flow = new GameObject("Level Flow")
                .AddComponent<LevelFlowController>();
            flow.ConfigureTotalSeeds(3);

            KoloController player = CreatePlayer();
            PlayerInputReader input = player.gameObject.AddComponent<PlayerInputReader>();
            input.Configure(player);

            CreateBlock("Start Cliff", new Vector2(-4f, -1f), new Vector2(10f, 2f), new Color(0.34f, 0.27f, 0.2f));
            CreateBlock("Puzzle Cliff", new Vector2(4f, -1f), new Vector2(6f, 2f), new Color(0.38f, 0.3f, 0.22f));
            CreateBlock("Upper Route", new Vector2(13f, 1f), new Vector2(6f, 1f), new Color(0.42f, 0.34f, 0.25f));
            CreateBlock("Lower Route", new Vector2(19f, -3f), new Vector2(8f, 1f), new Color(0.3f, 0.24f, 0.19f));
            CreateBlock("Finish Cliff", new Vector2(26f, -1f), new Vector2(8f, 2f), new Color(0.4f, 0.31f, 0.22f));
            CreateBlock("Step One", new Vector2(22f, -2f), new Vector2(2f, 1f), new Color(0.4f, 0.31f, 0.22f));
            CreateBlock("Step Two", new Vector2(23.5f, -1.5f), new Vector2(1f, 2f), new Color(0.4f, 0.31f, 0.22f));

            CreateHeavySource(new Vector2(1.5f, 0.35f));
            Rigidbody2D weight = CreateWeight(new Vector2(3f, 0.4f));

            GameObject platformObject = CreateBlock(
                "Hanging Platform",
                new Vector2(9f, -2f),
                new Vector2(3f, 0.5f),
                new Color(0.35f, 0.18f, 0.08f));
            HangingPlatform hanging = platformObject.AddComponent<HangingPlatform>();
            hanging.Configure(new Vector3(9f, 0.6f, 0f), 1.6f);

            GameObject plateObject = CreateBlock(
                "Pressure Plate",
                new Vector2(5f, 0.1f),
                new Vector2(1.6f, 0.2f),
                new Color(0.25f, 0.55f, 0.58f));
            PressurePlate plate = plateObject.AddComponent<PressurePlate>();
            plate.Configure(2f, hanging);

            GameObject breakableObject = CreateBlock(
                "Cracked Bridge",
                new Vector2(17f, 0.6f),
                new Vector2(2.2f, 0.35f),
                new Color(0.45f, 0.22f, 0.08f));
            breakableObject.AddComponent<BreakablePlatform>();

            CreateSeed(new Vector2(-1f, 0.6f), flow);
            CreateSeed(new Vector2(10f, 1.8f), flow);
            CreateSeed(new Vector2(24.5f, 0.8f), flow);
            CreateFinish(new Vector2(28f, 0.5f), flow);
            CreateCamera(player.transform);
            CreateTouchUI(input, flow);

            weight.WakeUp();
            flow.BeginLevel();
        }

        private static KoloController CreatePlayer()
        {
            GameObject player = new("Kolo");
            player.transform.position = new Vector3(-7f, 0.5f, 0f);
            Rigidbody2D body = player.AddComponent<Rigidbody2D>();
            body.gravityScale = 3f;
            body.freezeRotation = true;
            body.collisionDetectionMode = CollisionDetectionMode2D.Continuous;
            CapsuleCollider2D capsule = player.AddComponent<CapsuleCollider2D>();
            capsule.size = new Vector2(1f, 1.2f);
            SpriteRenderer renderer = player.AddComponent<SpriteRenderer>();
            renderer.sprite = WhiteSprite;
            renderer.color = new Color(0.82f, 0.49f, 0.18f);
            player.transform.localScale = new Vector3(1f, 1.2f, 1f);
            KoloController controller = player.AddComponent<KoloController>();
            player.AddComponent<KoloStateController>();
            return controller;
        }

        private static void CreateHeavySource(Vector2 position)
        {
            GameObject source = new("Heavy Water Source");
            source.transform.position = position;
            SpriteRenderer renderer = source.AddComponent<SpriteRenderer>();
            renderer.sprite = WhiteSprite;
            renderer.color = new Color(0.1f, 0.65f, 0.9f, 0.8f);
            source.transform.localScale = new Vector3(1.2f, 1.2f, 1f);
            CircleCollider2D trigger = source.AddComponent<CircleCollider2D>();
            trigger.isTrigger = true;
            source.AddComponent<HeavyStateSource>();
        }

        private static Rigidbody2D CreateWeight(Vector2 position)
        {
            GameObject weight = new("Pushable Stone");
            weight.transform.position = position;
            SpriteRenderer renderer = weight.AddComponent<SpriteRenderer>();
            renderer.sprite = WhiteSprite;
            renderer.color = new Color(0.3f, 0.32f, 0.35f);
            weight.transform.localScale = Vector3.one;
            weight.AddComponent<BoxCollider2D>();
            Rigidbody2D body = weight.AddComponent<Rigidbody2D>();
            body.mass = 2.5f;
            body.freezeRotation = true;
            return body;
        }

        private static GameObject CreateBlock(string name, Vector2 position, Vector2 size, Color color)
        {
            GameObject block = new(name);
            block.transform.position = position;
            block.transform.localScale = new Vector3(size.x, size.y, 1f);
            SpriteRenderer renderer = block.AddComponent<SpriteRenderer>();
            renderer.sprite = WhiteSprite;
            renderer.color = color;
            block.AddComponent<BoxCollider2D>();
            return block;
        }

        private static void CreateSeed(Vector2 position, LevelFlowController flow)
        {
            GameObject seed = new("Sesame Seed");
            seed.transform.position = position;
            seed.transform.localScale = new Vector3(0.35f, 0.5f, 1f);
            SpriteRenderer renderer = seed.AddComponent<SpriteRenderer>();
            renderer.sprite = WhiteSprite;
            renderer.color = new Color(1f, 0.78f, 0.2f);
            CircleCollider2D trigger = seed.AddComponent<CircleCollider2D>();
            trigger.isTrigger = true;
            SeedCollectible collectible = seed.AddComponent<SeedCollectible>();
            collectible.Configure(flow);
        }

        private static void CreateFinish(Vector2 position, LevelFlowController flow)
        {
            GameObject finish = new("Monastery Bell Finish");
            finish.transform.position = position;
            finish.transform.localScale = new Vector3(1f, 3f, 1f);
            SpriteRenderer renderer = finish.AddComponent<SpriteRenderer>();
            renderer.sprite = WhiteSprite;
            renderer.color = new Color(0.95f, 0.72f, 0.2f, 0.8f);
            BoxCollider2D trigger = finish.AddComponent<BoxCollider2D>();
            trigger.isTrigger = true;
            FinishTrigger finishTrigger = finish.AddComponent<FinishTrigger>();
            finishTrigger.Configure(flow);
        }

        private static void CreateCamera(Transform target)
        {
            GameObject cameraObject = new("Main Camera");
            cameraObject.tag = "MainCamera";
            UnityEngine.Camera camera = cameraObject.AddComponent<UnityEngine.Camera>();
            camera.orthographic = true;
            camera.orthographicSize = 5.5f;
            camera.backgroundColor = new Color(0.42f, 0.58f, 0.7f);
            cameraObject.transform.position = new Vector3(-4f, 1f, -10f);
            SideCameraFollow follow = cameraObject.AddComponent<SideCameraFollow>();
            follow.Configure(target, new Vector2(-4f, 26f), new Vector2(-2f, 5f));
        }

        private static void CreateBackground()
        {
            GameObject far = new("Meteora Background Placeholder");
            far.transform.position = new Vector3(10f, 4f, 5f);
            far.transform.localScale = new Vector3(45f, 18f, 1f);
            SpriteRenderer renderer = far.AddComponent<SpriteRenderer>();
            renderer.sprite = WhiteSprite;
            renderer.color = new Color(0.28f, 0.39f, 0.47f);
            renderer.sortingOrder = -20;
        }

        private static void CreateTouchUI(PlayerInputReader input, LevelFlowController flow)
        {
            GameObject eventSystem = new("EventSystem");
            eventSystem.AddComponent<EventSystem>();
            eventSystem.AddComponent<InputSystemUIInputModule>();

            GameObject canvasObject = new("Touch UI");
            Canvas canvas = canvasObject.AddComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            canvasObject.AddComponent<CanvasScaler>().uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            canvasObject.AddComponent<GraphicRaycaster>();

            CreateTouchButton(canvas.transform, "Left", new Vector2(80f, 80f), input, TouchAction.MoveLeft);
            CreateTouchButton(canvas.transform, "Right", new Vector2(190f, 80f), input, TouchAction.MoveRight);
            CreateTouchButton(canvas.transform, "Roll", new Vector2(-190f, 80f), input, TouchAction.Roll, true);
            CreateTouchButton(canvas.transform, "Jump", new Vector2(-80f, 80f), input, TouchAction.Jump, true);

            GameObject resultRoot = new("Result Panel");
            resultRoot.transform.SetParent(canvas.transform, false);
            Image panel = resultRoot.AddComponent<Image>();
            panel.color = new Color(0.05f, 0.08f, 0.1f, 0.88f);
            RectTransform rect = resultRoot.GetComponent<RectTransform>();
            rect.anchorMin = new Vector2(0.3f, 0.3f);
            rect.anchorMax = new Vector2(0.7f, 0.7f);
            rect.offsetMin = rect.offsetMax = Vector2.zero;
            Text title = CreateText(resultRoot.transform, new Vector2(0f, 60f), 28);
            Text seeds = CreateText(resultRoot.transform, Vector2.zero, 22);
            Text goals = CreateText(resultRoot.transform, new Vector2(0f, -45f), 18);
            ResultPanelController results = canvasObject.AddComponent<ResultPanelController>();
            results.Configure(resultRoot, title, seeds, goals);
            flow.LevelCompleted += results.ShowResult;
            resultRoot.SetActive(false);
        }

        private static void CreateTouchButton(
            Transform parent,
            string name,
            Vector2 anchoredPosition,
            PlayerInputReader input,
            TouchAction action,
            bool right = false)
        {
            GameObject button = new(name);
            button.transform.SetParent(parent, false);
            RectTransform rect = button.AddComponent<RectTransform>();
            rect.anchorMin = rect.anchorMax = right ? new Vector2(1f, 0f) : Vector2.zero;
            rect.sizeDelta = new Vector2(88f, 88f);
            rect.anchoredPosition = anchoredPosition;
            Image image = button.AddComponent<Image>();
            image.color = new Color(1f, 1f, 1f, 0.28f);
            button.AddComponent<TouchInputView>().Configure(input, action);
        }

        private static Text CreateText(Transform parent, Vector2 position, int size)
        {
            GameObject textObject = new("Text");
            textObject.transform.SetParent(parent, false);
            RectTransform rect = textObject.AddComponent<RectTransform>();
            rect.anchorMin = rect.anchorMax = new Vector2(0.5f, 0.5f);
            rect.sizeDelta = new Vector2(320f, 40f);
            rect.anchoredPosition = position;
            Text text = textObject.AddComponent<Text>();
            text.alignment = TextAnchor.MiddleCenter;
            text.fontSize = size;
            text.color = Color.white;
            text.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            return text;
        }

        private static Sprite WhiteSprite
        {
            get
            {
                if (whiteSprite == null)
                {
                    whiteSprite = Sprite.Create(
                        Texture2D.whiteTexture,
                        new Rect(0f, 0f, 1f, 1f),
                        new Vector2(0.5f, 0.5f),
                        1f);
                }

                return whiteSprite;
            }
        }
    }
}
