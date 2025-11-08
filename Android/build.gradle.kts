// Top-level build file where you can add configuration options common to all sub-projects/modules.
plugins {
    id("com.android.application") version "8.13.0" apply false
    id("com.android.library") version "8.13.0" apply false
    id("org.jetbrains.kotlin.android") version "1.9.20" apply false

    // THIS LINE IS THE FIX. It makes the Hilt plugin available to your app module.
    id("com.google.dagger.hilt.android") version "2.48" apply false
}
