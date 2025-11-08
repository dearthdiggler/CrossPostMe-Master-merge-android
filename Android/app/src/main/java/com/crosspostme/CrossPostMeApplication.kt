package com.crosspostme

import android.app.Application
import dagger.hilt.android.HiltAndroidApp

/**
 * Application class for CrossPostMe
 * Following Android best practices and Hilt dependency injection setup
 */
@HiltAndroidApp
class CrossPostMeApplication : Application() {
    
    override fun onCreate() {
        super.onCreate()
        // Application initialization code can go here
        // Following patterns from backend for proper logging and configuration
    }
}