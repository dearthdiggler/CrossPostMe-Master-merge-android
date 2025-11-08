package com.crosspostme.data.api

import com.crosspostme.data.model.*
import retrofit2.Response
import retrofit2.http.*

/**
 * API Service for AI features - matches backend routes from Copilot instructions
 * Following the backend API patterns: /api/ai prefix
 */
interface AIApiService {
    
    // AI-powered ad generation - POST /api/ai/generate-ad
    @POST("api/ai/generate-ad")
    suspend fun generateAd(@Body request: AIAdRequest): Response<AIAdResponse>
}

/**
 * API Service for Platform Management - matches backend routes
 * Following the backend API patterns: /api/platforms prefix
 */
interface PlatformsApiService {
    
    // Get All Platform Accounts - GET /api/platforms/
    @GET("api/platforms/")
    suspend fun getPlatformAccounts(): Response<List<PlatformAccount>>
    
    // Create Platform Account - POST /api/platforms/
    @POST("api/platforms/")
    suspend fun createPlatformAccount(@Body account: PlatformAccountCreate): Response<PlatformAccount>
    
    // Get Platform Account by ID - GET /api/platforms/{account_id}
    @GET("api/platforms/{account_id}")
    suspend fun getPlatformAccount(@Path("account_id") accountId: String): Response<PlatformAccount>
    
    // Update Platform Account - PUT /api/platforms/{account_id}
    @PUT("api/platforms/{account_id}")
    suspend fun updatePlatformAccount(
        @Path("account_id") accountId: String,
        @Body account: PlatformAccountCreate
    ): Response<PlatformAccount>
    
    // Delete Platform Account - DELETE /api/platforms/{account_id}
    @DELETE("api/platforms/{account_id}")
    suspend fun deletePlatformAccount(@Path("account_id") accountId: String): Response<Map<String, String>>
    
    // Test Platform Connection - POST /api/platforms/{account_id}/test
    @POST("api/platforms/{account_id}/test")
    suspend fun testPlatformConnection(@Path("account_id") accountId: String): Response<Map<String, Any>>
}

/**
 * API Service for Messages and Leads - matches backend routes
 * Following the backend API patterns: /api/messages prefix
 */
interface MessagesApiService {
    
    // Get All Messages - GET /api/messages/
    @GET("api/messages/")
    suspend fun getMessages(
        @Query("platform") platform: String? = null,
        @Query("is_read") isRead: Boolean? = null,
        @Query("priority") priority: String? = null
    ): Response<List<IncomingMessage>>
    
    // Create Message - POST /api/messages/
    @POST("api/messages/")
    suspend fun createMessage(@Body message: IncomingMessageCreate): Response<IncomingMessage>
    
    // Get Message by ID - GET /api/messages/{message_id}
    @GET("api/messages/{message_id}")
    suspend fun getMessage(@Path("message_id") messageId: String): Response<IncomingMessage>
    
    // Mark Message as Read - PUT /api/messages/{message_id}/read
    @PUT("api/messages/{message_id}/read")
    suspend fun markMessageAsRead(@Path("message_id") messageId: String): Response<IncomingMessage>
    
    // Get All Leads - GET /api/leads/
    @GET("api/leads/")
    suspend fun getLeads(
        @Query("status") status: String? = null,
        @Query("platform") platform: String? = null
    ): Response<List<Lead>>
    
    // Create Lead - POST /api/leads/
    @POST("api/leads/")
    suspend fun createLead(@Body lead: LeadCreate): Response<Lead>
    
    // Update Lead - PUT /api/leads/{lead_id}
    @PUT("api/leads/{lead_id}")
    suspend fun updateLead(
        @Path("lead_id") leadId: String,
        @Body leadUpdate: LeadUpdate
    ): Response<Lead>
}