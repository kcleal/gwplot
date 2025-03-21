
cdef extern from "GLFW/glfw3.h" nogil:
    int glfwInit()
    void glfwTerminate()
    int glfwGetKeyScancode(int GLFW_KEY)