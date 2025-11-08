package com.crosspostme.crosspostme.models

data class User(
    val id: Int,
    val username: String,
    val email: String,
    val isActive: Boolean
)
