using Kolo.Input;
using UnityEngine;
using UnityEngine.EventSystems;

namespace Kolo.UI
{
    public enum TouchAction
    {
        MoveLeft,
        MoveRight,
        Jump,
        Roll,
        Interact
    }

    [DisallowMultipleComponent]
    public sealed class TouchInputView : MonoBehaviour, IPointerDownHandler, IPointerUpHandler
    {
        [SerializeField] private PlayerInputReader input;
        [SerializeField] private TouchAction action;

        public void Configure(PlayerInputReader reader, TouchAction touchAction)
        {
            input = reader;
            action = touchAction;
        }

        public void OnPointerDown(PointerEventData eventData)
        {
            if (input == null)
            {
                return;
            }

            switch (action)
            {
                case TouchAction.MoveLeft:
                    input.SetTouchMove(-1f);
                    break;
                case TouchAction.MoveRight:
                    input.SetTouchMove(1f);
                    break;
                case TouchAction.Jump:
                    input.PressTouchJump();
                    break;
                case TouchAction.Roll:
                    input.SetTouchRoll(true);
                    break;
                case TouchAction.Interact:
                    input.PressTouchInteract();
                    break;
            }
        }

        public void OnPointerUp(PointerEventData eventData)
        {
            if (input == null)
            {
                return;
            }

            if (action is TouchAction.MoveLeft or TouchAction.MoveRight)
            {
                input.SetTouchMove(0f);
            }
            else if (action == TouchAction.Roll)
            {
                input.SetTouchRoll(false);
            }
        }
    }
}
