using Kolo.Player;
using UnityEngine;
using UnityEngine.InputSystem;

namespace Kolo.Input
{
    [DisallowMultipleComponent]
    public sealed class PlayerInputReader : MonoBehaviour
    {
        [SerializeField] private KoloController target;

        private float touchMoveAxis;
        private bool touchRollHeld;
        private bool touchJumpQueued;
        private bool touchInteractQueued;

        public float MoveAxis { get; private set; }
        public bool JumpPressedThisFrame { get; private set; }
        public bool RollHeld { get; private set; }
        public bool InteractPressedThisFrame { get; private set; }

        private void Update()
        {
            ReadDevices();
            target?.SetInput(
                MoveAxis,
                JumpPressedThisFrame,
                RollHeld,
                InteractPressedThisFrame);

            touchJumpQueued = false;
            touchInteractQueued = false;
        }

        public void SetTouchMove(float axis)
        {
            touchMoveAxis = Mathf.Clamp(axis, -1f, 1f);
        }

        public void SetTouchRoll(bool held)
        {
            touchRollHeld = held;
        }

        public void PressTouchJump()
        {
            touchJumpQueued = true;
        }

        public void PressTouchInteract()
        {
            touchInteractQueued = true;
        }

        private void ReadDevices()
        {
            float deviceMove = 0f;
            bool deviceJump = false;
            bool deviceRoll = false;
            bool deviceInteract = false;

            if (Keyboard.current != null)
            {
                deviceMove += Keyboard.current.aKey.isPressed || Keyboard.current.leftArrowKey.isPressed ? -1f : 0f;
                deviceMove += Keyboard.current.dKey.isPressed || Keyboard.current.rightArrowKey.isPressed ? 1f : 0f;
                deviceJump = Keyboard.current.spaceKey.wasPressedThisFrame;
                deviceRoll = Keyboard.current.sKey.isPressed
                    || Keyboard.current.downArrowKey.isPressed
                    || Keyboard.current.leftCtrlKey.isPressed;
                deviceInteract = Keyboard.current.eKey.wasPressedThisFrame;
            }

            if (Gamepad.current != null)
            {
                float stickMove = Gamepad.current.leftStick.x.ReadValue();
                float dpadMove = Gamepad.current.dpad.x.ReadValue();
                deviceMove = Mathf.Abs(stickMove) > Mathf.Abs(deviceMove) ? stickMove : deviceMove;
                deviceMove = Mathf.Abs(dpadMove) > Mathf.Abs(deviceMove) ? dpadMove : deviceMove;
                deviceJump |= Gamepad.current.buttonSouth.wasPressedThisFrame;
                deviceRoll |= Gamepad.current.buttonEast.isPressed;
                deviceInteract |= Gamepad.current.buttonWest.wasPressedThisFrame;
            }

            MoveAxis = Mathf.Abs(touchMoveAxis) > Mathf.Abs(deviceMove)
                ? touchMoveAxis
                : Mathf.Clamp(deviceMove, -1f, 1f);
            JumpPressedThisFrame = touchJumpQueued || deviceJump;
            RollHeld = touchRollHeld || deviceRoll;
            InteractPressedThisFrame = touchInteractQueued || deviceInteract;
        }
    }
}
