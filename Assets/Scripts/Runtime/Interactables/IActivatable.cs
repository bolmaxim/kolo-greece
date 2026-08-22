namespace Kolo.Interactables
{
    public interface IActivatable
    {
        bool IsActive { get; }
        void SetActive(bool active);
    }
}
